// 気象庁の警報注意報 r8 エンドポイント(bosai/warning/data/r8/{code}.json)の配信履歴から、
// 「現在この地域で有効な警報注意報」を再構成する。
//
// pipelines/warning/fetch_warning.py と同じ処理(同じ出力形式)をブラウザ側に移したもの。
// 旧エンドポイント(bosai/warning/data/warning/{code}.json)は2026年5月で更新が止まっており、
// r8 は「直近の発表いくつかぶんの配信履歴」を配列で返す。1件は特定の現象だけを更新する差分的な
// 内容のことが多いので、時系列順にマージして現在の状態を作る必要がある。
//
// 出力の形は旧フォーマット(areaTypes[].areas[].{code, warnings:[{code, status}]})に合わせてあり、
// GitHub上のバックアップJSON(パイプラインの出力)とそのまま差し替えられる。

export const NO_WARNING_STATUS = '発表警報・注意報はなし';

type Kind = { code?: string; status?: string };
type Item = { areaCode: string; kinds?: Kind[] };
export type WarningReport = {
	reportDatetime: string;
	headlineText?: string | null;
	warning?: { class10Items?: Item[]; class20Items?: Item[] };
};
export type WarningArea = { code: string; warnings: { code?: string; status: string }[] };
export type OfficeWarning = {
	reportDatetime: string | null;
	headlineText: string | null;
	areaTypes: { areas: WarningArea[] }[];
};

// reports(reportDatetime昇順)を area_code -> {warning_code: status} にマージする。
//
// レポート1件は「特定の現象1つぶんの状態変化」を表す配信単位で、その現象に関係しない地域には
// code なしの「発表警報・注意報はなし」が並ぶ(=その現象については対象外、という意味であって
// 「この地域は他の現象も含めて何も出ていない」という意味ではない)。そのため code なしの kind は
// 無視し(状態をリセットしない)、code ありの kind だけをマージしていく。ある現象が解除されれば
// code は残したまま status が「解除」に更新されるので、表示側の isActiveStatus() で除外できる。
//
// 並びの順序をパイプライン(Python)と揃えるため、Object ではなく Map を使う
// (Object だと "10" のような整数風のキーが先頭に並び替えられてしまう)。
function mergeAreaType(reports: WarningReport[], itemKey: 'class10Items' | 'class20Items'): WarningArea[] {
	const areaStates = new Map<string, Map<string, string>>();
	const allAreaCodes: string[] = [];

	for (const report of reports) {
		for (const item of report.warning?.[itemKey] ?? []) {
			if (!areaStates.has(item.areaCode)) {
				areaStates.set(item.areaCode, new Map());
				allAreaCodes.push(item.areaCode);
			}
			for (const kind of item.kinds ?? []) {
				if (!kind.code || !kind.status) continue;
				areaStates.get(item.areaCode)!.set(kind.code, kind.status);
			}
		}
	}

	return allAreaCodes.map((areaCode) => {
		const state = areaStates.get(areaCode)!;
		const warnings = Array.from(state, ([code, status]) => ({ code, status }));
		return { code: areaCode, warnings: warnings.length > 0 ? warnings : [{ status: NO_WARNING_STATUS }] };
	});
}

// r8 のレスポンス(配列)から、警報注意報の現在の状態を作る。想定外の形(配列でない・空)のときは
// 例外を投げる。呼び出し側はそれをバックアップ表示への切り替えの合図にする
// (空の配列を「警報なし」と読み違えて、出ている警報を見落とさないため)。
export function buildOfficeWarning(reports: unknown): OfficeWarning {
	if (!Array.isArray(reports) || reports.length === 0) {
		throw new Error('unexpected r8 response');
	}
	const sorted = [...(reports as WarningReport[])].sort((a, b) =>
		a.reportDatetime < b.reportDatetime ? -1 : a.reportDatetime > b.reportDatetime ? 1 : 0,
	);
	const latest = sorted[sorted.length - 1];
	return {
		reportDatetime: latest.reportDatetime ?? null,
		headlineText: latest.headlineText ?? null,
		areaTypes: [{ areas: mergeAreaType(sorted, 'class10Items') }, { areas: mergeAreaType(sorted, 'class20Items') }],
	};
}
