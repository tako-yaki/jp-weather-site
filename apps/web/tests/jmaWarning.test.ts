// 警報注意報の再構成(src/lib/jmaWarning.ts)のテスト。実行: npm test
// 実データでは、全58地域でパイプライン(pipelines/warning/fetch_warning.py)の出力と完全一致することを確認済み。
import test from 'node:test';
import assert from 'node:assert/strict';
import { buildOfficeWarning, NO_WARNING_STATUS } from '../src/lib/jmaWarning.ts';

const report = (reportDatetime: string, class10Items: any[], class20Items: any[] = []) => ({
	reportDatetime,
	headlineText: `h-${reportDatetime}`,
	warning: { class10Items, class20Items },
});

test('配信履歴を時系列順にマージし、後の発表が前の状態を上書きする', () => {
	const out = buildOfficeWarning([
		// 配列の順序が逆でも reportDatetime の昇順で処理される
		report('2026-10-04T12:00:00+09:00', [{ areaCode: '130010', kinds: [{ code: '10', status: '解除' }] }]),
		report('2026-10-04T09:00:00+09:00', [{ areaCode: '130010', kinds: [{ code: '10', status: '発表' }] }]),
	]);
	assert.deepEqual(out.areaTypes[0].areas, [{ code: '130010', warnings: [{ code: '10', status: '解除' }] }]);
	assert.equal(out.reportDatetime, '2026-10-04T12:00:00+09:00');
	assert.equal(out.headlineText, 'h-2026-10-04T12:00:00+09:00');
});

test('codeなしの「発表警報・注意報はなし」は、他の現象の状態をリセットしない', () => {
	const out = buildOfficeWarning([
		report('2026-10-04T09:00:00+09:00', [{ areaCode: '130010', kinds: [{ code: '10', status: '発表' }] }]),
		report('2026-10-04T10:00:00+09:00', [{ areaCode: '130010', kinds: [{ status: NO_WARNING_STATUS }] }]),
	]);
	assert.deepEqual(out.areaTypes[0].areas[0].warnings, [{ code: '10', status: '発表' }]);
});

test('現象が何もない地域は「発表警報・注意報はなし」になる', () => {
	const out = buildOfficeWarning([report('2026-10-04T09:00:00+09:00', [{ areaCode: '130020', kinds: [{ status: NO_WARNING_STATUS }] }])]);
	assert.deepEqual(out.areaTypes[0].areas, [{ code: '130020', warnings: [{ status: NO_WARNING_STATUS }] }]);
});

test('現象コードの並びは発表順のまま(整数風のキー "10" が先頭に並び替えられない)', () => {
	const out = buildOfficeWarning([
		report('2026-10-04T09:00:00+09:00', [{ areaCode: '130010', kinds: [{ code: '21', status: '発表' }] }]),
		report('2026-10-04T10:00:00+09:00', [{ areaCode: '130010', kinds: [{ code: '03', status: '発表' }] }]),
		report('2026-10-04T11:00:00+09:00', [{ areaCode: '130010', kinds: [{ code: '10', status: '発表' }] }]),
	]);
	assert.deepEqual(out.areaTypes[0].areas[0].warnings.map((w) => w.code), ['21', '03', '10']);
});

test('class10 と class20 は別々にマージされる', () => {
	const out = buildOfficeWarning([
		report('2026-10-04T09:00:00+09:00', [{ areaCode: '130010', kinds: [{ code: '10', status: '発表' }] }], [
			{ areaCode: '1310100', kinds: [{ code: '14', status: '発表' }] },
		]),
	]);
	assert.equal(out.areaTypes[0].areas[0].code, '130010');
	assert.equal(out.areaTypes[1].areas[0].code, '1310100');
});

test('想定外の形(配列でない・空)は例外にする(警報なしと誤認しないため)', () => {
	assert.throws(() => buildOfficeWarning([]));
	assert.throws(() => buildOfficeWarning({}));
	assert.throws(() => buildOfficeWarning(null));
});
