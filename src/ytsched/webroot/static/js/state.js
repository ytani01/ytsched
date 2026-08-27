/**
 *   (c) 2026 ytani01
 */

// ファイルをまたいで参照・更新する状態 (TODO-083)。他のスクリプトから
// ``ytState.xxx`` の形で読み書きする
const ytState = {
    elLoadingSpinner: null,
    elMain: null,
    elGaugeR0: null,
    elWeekWrap: null,
    // いま見ている週が、最初に描かれた週から何週ぶん離れているか
    // (TODO-069)。``.my-week-panel`` の ``data-offset`` と同じ数え方で、
    // 読み込んだ直後は 0
    activeWeekOffset: 0,
};
