// ブラウザから直接取得するデータ群。
//
// 警報注意報・アメダス実況は数分おき、天気予報テキストは2〜3時間おきに更新されるが、
// Astroの静的ビルドは天気予報テキストのときしか走らない(Cloudflareの無料枠が月500ビルドまでのため)。
// そのため警報・アメダス・Open-Meteo系のデータはビルド時にHTMLへ焼き込まず、
// ページを開いたブラウザが都度これらの関数で直接取得する。
//
// 警報・アメダスは、まず気象庁の公開JSONから直接取得する(CORS許可・max-age=60を確認済み。
// GitHub Actionsのcronの遅れ・欠落や、raw.githubusercontent.comのキャッシュ(5分)に左右されない)。
// 気象庁の取得に失敗したとき(通信障害・形式変更など)だけ、パイプラインがGitHubに置いている
// バックアップのJSONに切り替える。
import { GITHUB_RAW_DATA_BASE } from '../config';
import { buildOfficeWarning, type OfficeWarning } from './jmaWarning';

const OPEN_METEO_BASE = 'https://api.open-meteo.com/v1/forecast';
const JMA_BASE = 'https://www.jma.go.jp/bosai';
const FETCH_TIMEOUT_MS = 8000;

// revalidate: リアルタイム性が要るデータ(警報・アメダス)では、ブラウザのHTTPキャッシュ(max-age=60)を
// そのまま使わず、毎回サーバー(CDN)に更新有無を確認する(未更新なら304で、転送量はほぼゼロ)。
// これで「気象庁側が更新してから最大 約1分(CDNのキャッシュ) + こちらのポーリング間隔」で反映される。
function fetchWithTimeout(url: string, revalidate = false): Promise<Response> {
	return fetch(url, {
		cache: revalidate ? 'no-cache' : 'default',
		signal: typeof AbortSignal.timeout === 'function' ? AbortSignal.timeout(FETCH_TIMEOUT_MS) : undefined,
	});
}

async function getJson(url: string, revalidate = false): Promise<any> {
	const res = await fetchWithTimeout(url, revalidate);
	if (!res.ok) throw new Error(`${url}: ${res.status}`);
	return res.json();
}

// source: 'jma' = 気象庁から直接取得 / 'backup' = GitHub上のバックアップ(最新でない可能性がある)
export type WarningResult = OfficeWarning & { source: 'jma' | 'backup' };

export async function fetchOfficeWarning(officeCode: string): Promise<WarningResult> {
	try {
		const reports = await getJson(`${JMA_BASE}/warning/data/r8/${officeCode}.json`, true);
		return { ...buildOfficeWarning(reports), source: 'jma' };
	} catch {
		const backup = await getJson(`${GITHUB_RAW_DATA_BASE}/warning/${officeCode}.json`, true);
		return { ...backup, source: 'backup' };
	}
}

// アメダスの最新観測時刻(例: "2026-10-04T22:10:00+09:00")。数バイトで、10分ごとの観測の更新有無を確かめるのに使う。
export async function fetchAmedasLatestTime(): Promise<string> {
	const res = await fetchWithTimeout(`${JMA_BASE}/amedas/data/latest_time.txt`, true);
	if (!res.ok) throw new Error(`latest_time: ${res.status}`);
	const latest = (await res.text()).trim();
	if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d/.test(latest)) throw new Error('unexpected latest_time format');
	return latest;
}

// アメダス1地点の最新観測。戻り値の形は従来(全国ぶんの amedas-current.json)と同じ
// { observedAt, stations: { 地点コード: 観測値 } } にしてあり、stations には要求した地点だけが入る。
// 全国ぶんのmapファイルは約250KBあるが、地点別ファイルは約4KBで済むので、そちらを使う。
// latestTime: 直前にfetchAmedasLatestTime()で取得済みなら渡す(同じ確認を二重にしないため)。
export async function fetchAmedasCurrent(
	stationCode: string,
	latestTime?: string,
): Promise<{ observedAt: string; stations: Record<string, any> }> {
	try {
		const observedAt = latestTime ?? (await fetchAmedasLatestTime());
		const [, y, mo, d, h, mi] = observedAt.match(/^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)/)!;
		// 地点別ファイルは3時間単位(00,03,...,21)。ファイル内は10分刻みの観測時刻がキー。
		const block = String(Math.floor(Number(h) / 3) * 3).padStart(2, '0');
		const points = await getJson(`${JMA_BASE}/amedas/data/point/${stationCode}/${y}${mo}${d}_${block}.json`, true);
		const entry = points?.[`${y}${mo}${d}${h}${mi}00`];
		if (!entry) throw new Error('no entry for latest time');
		return { observedAt, stations: { [stationCode]: entry } };
	} catch {
		return getJson(`${GITHUB_RAW_DATA_BASE}/amedas-current.json`, true);
	}
}

// 現況・時間別・当面(3日ぶん)の日別データ。pipelines/openmeteo/fetch_openmeteo.py と
// 同じパラメータにして、レスポンス形状を揃えている。
export async function fetchRegionOpenMeteo(lat: number, lon: number): Promise<any> {
	const params = new URLSearchParams({
		latitude: String(lat),
		longitude: String(lon),
		current: 'temperature_2m,relative_humidity_2m,precipitation,weathercode,windspeed_10m,winddirection_10m',
		hourly: 'temperature_2m,precipitation,weathercode,windspeed_10m,winddirection_10m',
		daily: 'sunrise,sunset,temperature_2m_max,temperature_2m_min',
		timezone: 'Asia/Tokyo',
		forecast_days: '3',
		wind_speed_unit: 'ms', // アメダス実況(m/s)と単位を揃える(Open-Meteoの既定はkm/h)
	});
	const res = await fetch(`${OPEN_METEO_BASE}?${params}`);
	if (!res.ok) throw new Error(`open-meteo fetch failed: ${res.status}`);
	return res.json();
}

// 10日間予報の8〜10日目を補うための長期日別データ。
// pipelines/openmeteo/fetch_openmeteo_extended.py と同じパラメータ。
export async function fetchRegionOpenMeteoExtended(lat: number, lon: number): Promise<any> {
	const params = new URLSearchParams({
		latitude: String(lat),
		longitude: String(lon),
		daily: 'weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max',
		timezone: 'Asia/Tokyo',
		forecast_days: '12',
	});
	const res = await fetch(`${OPEN_METEO_BASE}?${params}`);
	if (!res.ok) throw new Error(`open-meteo extended fetch failed: ${res.status}`);
	return res.json();
}
