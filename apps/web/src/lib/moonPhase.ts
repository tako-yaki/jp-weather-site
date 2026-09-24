// 月齢の近似計算（外部APIを使わない自己完結の天文計算）。
// 既知の新月時刻を基準に、朔望月（29.53058867日）で割った余りから月齢を求める標準的な方法。
// 精度は概ね±1日程度で、表示用途としては十分。
const SYNODIC_MONTH_DAYS = 29.53058867;
const KNOWN_NEW_MOON_UTC = Date.UTC(2000, 0, 6, 18, 14); // 2000-01-06 18:14 UTC

export interface MoonPhase {
	age: number; // 0 〜 29.53
	illumination: number; // 0 〜 100 (%)
	label: string;
	icon: string;
}

export function getMoonPhase(date: Date): MoonPhase {
	const diffDays = (date.getTime() - KNOWN_NEW_MOON_UTC) / 86_400_000;
	const age = ((diffDays % SYNODIC_MONTH_DAYS) + SYNODIC_MONTH_DAYS) % SYNODIC_MONTH_DAYS;
	const illumination = (1 - Math.cos((2 * Math.PI * age) / SYNODIC_MONTH_DAYS)) / 2;

	const steps: Array<{ max: number; label: string; icon: string }> = [
		{ max: 1.84, label: '新月', icon: '🌑' },
		{ max: 5.53, label: '三日月', icon: '🌒' },
		{ max: 9.22, label: '上弦の月', icon: '🌓' },
		{ max: 12.91, label: '十三夜月', icon: '🌔' },
		{ max: 16.61, label: '満月', icon: '🌕' },
		{ max: 20.30, label: '十六夜月', icon: '🌖' },
		{ max: 23.99, label: '下弦の月', icon: '🌗' },
		{ max: 27.68, label: '有明月', icon: '🌘' },
		{ max: SYNODIC_MONTH_DAYS, label: '新月', icon: '🌑' },
	];
	const step = steps.find((s) => age <= s.max) ?? steps[steps.length - 1];

	return {
		age,
		illumination: Math.round(illumination * 100),
		label: step.label,
		icon: step.icon,
	};
}
