// ブラウザから直接取得するデータ群。
//
// 警報注意報・アメダス実況は5分おき、天気予報テキストは2〜3時間おきに更新されるが、
// Astroの静的ビルドは天気予報テキストのときしか走らない(Cloudflare Pagesの無料枠が
// 月500ビルドまでのため)。そのため警報・アメダス・Open-Meteo系のデータはビルド時に
// HTMLへ焼き込まず、ページを開いたブラウザが都度これらの関数で直接取得する。
import { GITHUB_RAW_DATA_BASE } from '../config';

const OPEN_METEO_BASE = 'https://api.open-meteo.com/v1/forecast';

export async function fetchOfficeWarning(officeCode: string): Promise<any> {
	const res = await fetch(`${GITHUB_RAW_DATA_BASE}/warning/${officeCode}.json`);
	if (!res.ok) throw new Error(`warning fetch failed: ${res.status}`);
	return res.json();
}

export async function fetchAmedasCurrent(): Promise<any> {
	const res = await fetch(`${GITHUB_RAW_DATA_BASE}/amedas-current.json`);
	if (!res.ok) throw new Error(`amedas-current fetch failed: ${res.status}`);
	return res.json();
}

// 現況・時間別・当面(3日ぶん)の日別データ。pipelines/openmeteo/fetch_openmeteo.py と
// 同じパラメータにして、レスポンス形状を揃えている。
export async function fetchRegionOpenMeteo(lat: number, lon: number): Promise<any> {
	const params = new URLSearchParams({
		latitude: String(lat),
		longitude: String(lon),
		current: 'temperature_2m,relative_humidity_2m,precipitation,weathercode',
		hourly: 'temperature_2m,precipitation,weathercode',
		daily: 'sunrise,sunset,temperature_2m_max,temperature_2m_min',
		timezone: 'Asia/Tokyo',
		forecast_days: '3',
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
