// 気象庁 警報・注意報コード。
// 実データ（headlineText と code の突き合わせ、および NII 特別警報・警報・注意報データベース
// https://agora.ex.nii.ac.jp/cps/weather/warning/stat/{code}/ の見出しとの突き合わせ）で
// 確認できたものだけを載せている。未確認のコードは推測でラベルを付けず、コード番号のまま表示する。
// 全コード表は気象庁防災情報XMLの「警報等情報要素コード管理表」を要確認。
const WARNING_CODE_TABLE: Record<string, string> = {
	'03': '大雨警報',
	'10': '大雨注意報',
	'14': '雷注意報',
	'15': '強風注意報',
	'16': '波浪注意報',
	'17': '融雪注意報',
	'19': '高潮注意報',
	'20': '濃霧注意報',
	'21': '乾燥注意報',
	'22': 'なだれ注意報',
	'24': '霜注意報',
	// 29/48/49 は2026年5月の防災気象情報の体系変更で新設された「危険警報」等の階級。
	'29': '土砂災害注意報',
	'48': '高潮危険警報',
	'49': '土砂災害危険警報',
};

export function describeWarningCode(code: string): string {
	return WARNING_CODE_TABLE[code] ?? `注意報・警報コード${code}（要確認）`;
}

export function isActiveStatus(status: string): boolean {
	return status !== '発表警報・注意報はなし' && status !== '解除';
}
