// 16方位ラベル。北を起点に時計回り。
const DIRECTIONS_16 = [
	'北', '北北東', '北東', '東北東', '東', '東南東', '南東', '南南東',
	'南', '南南西', '南西', '西南西', '西', '西北西', '北西', '北北西',
];

// Open-Meteoの winddirection_10m(度、気象学的な「吹いてくる方向」)から16方位ラベルを引く。
export function degreesToDirection16(deg: number): string {
	const idx = Math.round((((deg % 360) + 360) % 360) / 22.5) % 16;
	return DIRECTIONS_16[idx];
}

// 気象庁アメダスの windDirection は 0=静穏、1=北北東〜16=北 の16方位コード(1刻み=22.5度、時計回り)。
// 参考: https://qiita.com/KAI_Mutsumi/items/79b169d0b8ed3135cd1a
// 0(静穏)はコード上ではnullを返す(方位自体が存在しないため)。
export function amedasWindDirectionLabel(code: number): string | null {
	if (!code) return null;
	return degreesToDirection16(code * 22.5);
}
