// 気象庁 天気コード（weatherCode）の表示用マッピング。
// 網羅リストではなく、実データ(コードと天気テキストの組)で確認できたものだけを載せている。
// 気象庁が公開しているコード表の原本は見つけられなかったため、記憶や推測で足さない。
// 表にないコードは、天気テキストがあればそれをそのまま表示し(短期予報)、無ければ先頭桁で分類する(週間予報)。
export type WeatherCategory = 'sun' | 'cloud' | 'rain' | 'snow' | 'unknown';

interface WeatherCodeInfo {
	label: string;
	icon: string;
	category: WeatherCategory;
}

const CODE_TABLE: Record<string, WeatherCodeInfo> = {
	'100': { label: '晴れ', icon: '☀️', category: 'sun' },
	'101': { label: '晴れ時々くもり', icon: '🌤️', category: 'sun' },
	'102': { label: '晴れ一時雨', icon: '🌦️', category: 'sun' },
	'103': { label: '晴れ時々雨', icon: '🌦️', category: 'sun' },
	'110': { label: '晴れ後時々くもり', icon: '🌤️', category: 'sun' },
	'111': { label: '晴れ後くもり', icon: '🌥️', category: 'sun' },
	'112': { label: '晴れ後一時雨', icon: '🌦️', category: 'sun' },
	'113': { label: '晴れ後時々雨', icon: '🌦️', category: 'sun' },
	'114': { label: '晴れ後雨', icon: '🌧️', category: 'sun' },
	'200': { label: 'くもり', icon: '☁️', category: 'cloud' },
	'201': { label: 'くもり時々晴れ', icon: '⛅', category: 'cloud' },
	'202': { label: 'くもり一時雨', icon: '🌦️', category: 'cloud' },
	'203': { label: 'くもり時々雨', icon: '🌦️', category: 'cloud' },
	'204': { label: 'くもり一時雪', icon: '🌨️', category: 'cloud' },
	'205': { label: 'くもり時々雪', icon: '🌨️', category: 'cloud' },
	'210': { label: 'くもり後時々晴れ', icon: '⛅', category: 'cloud' },
	'211': { label: 'くもり後晴れ', icon: '⛅', category: 'cloud' },
	'212': { label: 'くもり後一時雨', icon: '🌦️', category: 'cloud' },
	'213': { label: 'くもり後時々雨', icon: '🌦️', category: 'cloud' },
	'214': { label: 'くもり後雨', icon: '🌧️', category: 'cloud' },
	'300': { label: '雨', icon: '🌧️', category: 'rain' },
	'301': { label: '雨時々晴れ', icon: '🌦️', category: 'rain' },
	'302': { label: '雨時々止む', icon: '🌧️', category: 'rain' },
	'303': { label: '雨時々雪', icon: '🌨️', category: 'rain' },
	'311': { label: '雨後晴れ', icon: '🌦️', category: 'rain' },
	'313': { label: '雨後くもり', icon: '🌧️', category: 'rain' },
	'400': { label: '雪', icon: '❄️', category: 'snow' },
	'401': { label: '雪時々晴れ', icon: '🌨️', category: 'snow' },
	'402': { label: '雪時々止む', icon: '❄️', category: 'snow' },
	'411': { label: '雪後晴れ', icon: '🌨️', category: 'snow' },
	'413': { label: '雪後くもり', icon: '🌨️', category: 'snow' },
};

const CATEGORY_FALLBACK: Record<string, WeatherCodeInfo> = {
	'1': { label: '晴れ系', icon: '☀️', category: 'sun' },
	'2': { label: 'くもり系', icon: '☁️', category: 'cloud' },
	'3': { label: '雨', icon: '🌧️', category: 'rain' },
	'4': { label: '雪', icon: '❄️', category: 'snow' },
};

// text: 気象庁の天気テキスト(短期予報のweathers。全角スペース区切り)。表に無いコードのときだけ使う。
export function describeWeatherCode(code: string, text?: string): WeatherCodeInfo {
	if (CODE_TABLE[code]) return CODE_TABLE[code];
	const firstDigit = code[0];
	if (CATEGORY_FALLBACK[firstDigit]) {
		const fallback = CATEGORY_FALLBACK[firstDigit];
		const detail = text?.replace(/[\s\u3000]+/g, '');
		return detail ? { ...fallback, label: detail } : fallback;
	}
	return { label: `不明(${code})`, icon: '❔', category: 'unknown' };
}
