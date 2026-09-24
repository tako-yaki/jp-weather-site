// Open-Meteo が返す WMO (世界気象機関) 天気コードの表示用マッピング。
// 参照: https://open-meteo.com/en/docs (WMO Weather interpretation codes)
export type WeatherCategory = 'sun' | 'cloud' | 'rain' | 'snow' | 'fog';

interface WmoCodeInfo {
	label: string;
	dayIcon: string;
	nightIcon: string;
	category: WeatherCategory;
}

const WMO_TABLE: Record<number, WmoCodeInfo> = {
	0: { label: '快晴', dayIcon: '☀️', nightIcon: '🌙', category: 'sun' },
	1: { label: '晴れ', dayIcon: '🌤️', nightIcon: '🌙', category: 'sun' },
	2: { label: '晴れ時々くもり', dayIcon: '⛅', nightIcon: '☁️', category: 'cloud' },
	3: { label: 'くもり', dayIcon: '☁️', nightIcon: '☁️', category: 'cloud' },
	45: { label: '霧', dayIcon: '🌫️', nightIcon: '🌫️', category: 'fog' },
	48: { label: '霧氷', dayIcon: '🌫️', nightIcon: '🌫️', category: 'fog' },
	51: { label: '弱い霧雨', dayIcon: '🌦️', nightIcon: '🌧️', category: 'rain' },
	53: { label: '霧雨', dayIcon: '🌦️', nightIcon: '🌧️', category: 'rain' },
	55: { label: '強い霧雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	56: { label: '着氷性の弱い霧雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	57: { label: '着氷性の霧雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	61: { label: '弱い雨', dayIcon: '🌦️', nightIcon: '🌧️', category: 'rain' },
	63: { label: '雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	65: { label: '強い雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	66: { label: '着氷性の弱い雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	67: { label: '着氷性の雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	71: { label: '弱い雪', dayIcon: '🌨️', nightIcon: '🌨️', category: 'snow' },
	73: { label: '雪', dayIcon: '❄️', nightIcon: '❄️', category: 'snow' },
	75: { label: '強い雪', dayIcon: '❄️', nightIcon: '❄️', category: 'snow' },
	77: { label: '細氷', dayIcon: '❄️', nightIcon: '❄️', category: 'snow' },
	80: { label: 'にわか雨', dayIcon: '🌦️', nightIcon: '🌧️', category: 'rain' },
	81: { label: 'にわか雨', dayIcon: '🌦️', nightIcon: '🌧️', category: 'rain' },
	82: { label: '激しいにわか雨', dayIcon: '🌧️', nightIcon: '🌧️', category: 'rain' },
	85: { label: 'にわか雪', dayIcon: '🌨️', nightIcon: '🌨️', category: 'snow' },
	86: { label: '激しいにわか雪', dayIcon: '❄️', nightIcon: '❄️', category: 'snow' },
	95: { label: '雷雨', dayIcon: '⛈️', nightIcon: '⛈️', category: 'rain' },
	96: { label: '雷雨（ひょう）', dayIcon: '⛈️', nightIcon: '⛈️', category: 'rain' },
	99: { label: '雷雨（激しいひょう）', dayIcon: '⛈️', nightIcon: '⛈️', category: 'rain' },
};

export function describeWmoCode(code: number, isNight = false): WmoCodeInfo & { icon: string } {
	const info = WMO_TABLE[code] ?? { label: `不明(${code})`, dayIcon: '❔', nightIcon: '❔', category: 'cloud' as const };
	return { ...info, icon: isNight ? info.nightIcon : info.dayIcon };
}
