import { n as derived } from "../../chunks/dev.js";
//#region src/routes/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let mode = "";
		let tasks = [];
		let shuffledTasks = [];
		let currentIndex = 0;
		derived(() => tasks.length > 0);
		derived(() => shuffledTasks[currentIndex] ?? null);
		$$renderer.push(`<main class="svelte-1uha8ag"><div class="controls svelte-1uha8ag">`);
		$$renderer.select({
			value: mode,
			"aria-label": "mode"
		}, ($$renderer) => {
			$$renderer.option({ value: "" }, ($$renderer) => {});
			$$renderer.option({ value: "single-task" }, ($$renderer) => {
				$$renderer.push(`single task`);
			});
			$$renderer.option({ value: "exam" }, ($$renderer) => {
				$$renderer.push(`exam`);
			});
			$$renderer.option({ value: "shuffle-exam" }, ($$renderer) => {
				$$renderer.push(`shuffle exam`);
			});
		});
		$$renderer.push(` `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></main>`);
	});
}
//#endregion
export { _page as default };
