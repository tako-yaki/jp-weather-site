// 気象庁 警報・注意報コード。
// 実データ（headlineText と code の突き合わせ）で確認できたものだけを載せている。
// 未確認のコードは推測でラベルを付けず、コード番号のまま表示する。
// 全コード表は気象庁防災情報XMLの「警報等情報要素コード管理表」を要確認。
const WARNING_CODE_TABLE: Record<string, string> = {
	'14': '雷注意報',
	'15': '強風注意報',
	'16': '波浪注意報',
	'20': '濃霧注意報',
};

export function describeWarningCode(code: string): string {
	return WARNING_CODE_TABLE[code] ?? `注意報・警報コード${code}（要確認）`;
}

export function isActiveStatus(status: string): boolean {
	return status !== '発表警報・注意報はなし' && status !== '解除';
}
