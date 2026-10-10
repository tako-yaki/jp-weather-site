// 警報注意報・アメダス実況は、まず気象庁の公開JSONからブラウザが直接取得する(lib/clientData.ts)。
// ここで指定するのは、それが失敗したときのバックアップの場所: GitHub Actionsが定期的に
// 更新してpushしているJSONを、サイトの再ビルドなしで(raw contentは約5分キャッシュされる)読む。
export const GITHUB_RAW_DATA_BASE =
	'https://raw.githubusercontent.com/tako-yaki/jp-weather-site/main/apps/web/public/data';
