// 警報注意報・アメダス実況(5分おきに更新)は、サイトの再ビルドを起こさずに反映するため、
// ビルド時にHTMLへ焼き込まず、ブラウザから直接この場所のJSONを取得する。
// GitHub raw contentは push した瞬間に内容が更新される(ビルド不要)ので、この用途に向いている。
export const GITHUB_RAW_DATA_BASE =
	'https://raw.githubusercontent.com/tako-yaki/jp-weather-site/main/apps/web/public/data';
