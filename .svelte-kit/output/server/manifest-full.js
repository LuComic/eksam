export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["data/exams.json","data/extraction-report.json","data/tasks.json","generated/answers/2022-i-1-p1.png","generated/answers/2022-i-2-p2.png","generated/answers/2022-i-3-p3.png","generated/answers/2022-i-4-p4.png","generated/answers/2022-i-5-p5.png","generated/answers/2022-i-5-p6.png","generated/answers/2022-i-6-p7.png","generated/answers/2022-i-6-p8.png","generated/answers/2022-i-7-p9.png","generated/answers/2022-ii-10-p14.png","generated/answers/2022-ii-10-p15.png","generated/answers/2022-ii-11-p16.png","generated/answers/2022-ii-11-p17.png","generated/answers/2022-ii-12-p18.png","generated/answers/2022-ii-8-p10.png","generated/answers/2022-ii-8-p11.png","generated/answers/2022-ii-9-p12.png","generated/answers/2022-ii-9-p13.png","generated/answers/2023-i-1-p1.png","generated/answers/2023-i-2-p2.png","generated/answers/2023-i-3-p3.png","generated/answers/2023-i-4-p4.png","generated/answers/2023-i-5-p5.png","generated/answers/2023-i-5-p6.png","generated/answers/2023-i-6-p7.png","generated/answers/2023-i-7-p8.png","generated/answers/2023-ii-10-p12.png","generated/answers/2023-ii-11-p13.png","generated/answers/2023-ii-12-p14.png","generated/answers/2023-ii-8-p10.png","generated/answers/2023-ii-8-p9.png","generated/answers/2023-ii-9-p11.png","generated/answers/2024-i-1-p1.png","generated/answers/2024-i-2-p2.png","generated/answers/2024-i-3-p3.png","generated/answers/2024-i-4-p4.png","generated/answers/2024-i-5-p5.png","generated/answers/2024-i-5-p6.png","generated/answers/2024-i-6-p7.png","generated/answers/2024-i-6-p8.png","generated/answers/2024-i-7-p9.png","generated/answers/2024-ii-10-p13.png","generated/answers/2024-ii-11-p14.png","generated/answers/2024-ii-12-p15.png","generated/answers/2024-ii-8-p10.png","generated/answers/2024-ii-8-p11.png","generated/answers/2024-ii-9-p12.png","generated/answers/2025-i-1-p1.png","generated/answers/2025-i-2-p2.png","generated/answers/2025-i-3-p3.png","generated/answers/2025-i-4-p4.png","generated/answers/2025-i-5-p5.png","generated/answers/2025-i-5-p6.png","generated/answers/2025-i-6-p7.png","generated/answers/2025-i-7-p8.png","generated/answers/2025-ii-10-p13.png","generated/answers/2025-ii-11-p14.png","generated/answers/2025-ii-12-p15.png","generated/answers/2025-ii-8-p10.png","generated/answers/2025-ii-8-p9.png","generated/answers/2025-ii-9-p11.png","generated/answers/2025-ii-9-p12.png","generated/previews/review.html","generated/tasks/2021-i-1-p2.png","generated/tasks/2021-i-2-p2.png","generated/tasks/2021-i-3-p3.png","generated/tasks/2021-i-4-p3.png","generated/tasks/2021-i-5-p4.png","generated/tasks/2021-i-6-p5.png","generated/tasks/2021-i-7-p6.png","generated/tasks/2021-ii-10-p4.png","generated/tasks/2021-ii-11-p5.png","generated/tasks/2021-ii-12-p6.png","generated/tasks/2021-ii-8-p2.png","generated/tasks/2021-ii-9-p3.png","generated/tasks/2022-i-1-p2.png","generated/tasks/2022-i-2-p2.png","generated/tasks/2022-i-3-p3.png","generated/tasks/2022-i-4-p3.png","generated/tasks/2022-i-5-p4.png","generated/tasks/2022-i-6-p5.png","generated/tasks/2022-i-7-p6.png","generated/tasks/2022-ii-10-p4.png","generated/tasks/2022-ii-11-p5.png","generated/tasks/2022-ii-12-p6.png","generated/tasks/2022-ii-8-p2.png","generated/tasks/2022-ii-9-p3.png","generated/tasks/2023-i-1-p2.png","generated/tasks/2023-i-2-p2.png","generated/tasks/2023-i-3-p3.png","generated/tasks/2023-i-4-p3.png","generated/tasks/2023-i-5-p4.png","generated/tasks/2023-i-6-p5.png","generated/tasks/2023-i-7-p6.png","generated/tasks/2023-ii-10-p4.png","generated/tasks/2023-ii-11-p5.png","generated/tasks/2023-ii-12-p6.png","generated/tasks/2023-ii-8-p2.png","generated/tasks/2023-ii-9-p3.png","generated/tasks/2024-i-1-p2.png","generated/tasks/2024-i-2-p2.png","generated/tasks/2024-i-3-p3.png","generated/tasks/2024-i-4-p3.png","generated/tasks/2024-i-5-p4.png","generated/tasks/2024-i-6-p4.png","generated/tasks/2024-i-7-p3.png","generated/tasks/2024-ii-10-p4.png","generated/tasks/2024-ii-11-p4.png","generated/tasks/2024-ii-12-p3.png","generated/tasks/2024-ii-8-p2.png","generated/tasks/2024-ii-9-p3.png","generated/tasks/2025-i-1-p2.png","generated/tasks/2025-i-2-p2.png","generated/tasks/2025-i-3-p3.png","generated/tasks/2025-i-4-p3.png","generated/tasks/2025-i-5-p4.png","generated/tasks/2025-i-6-p5.png","generated/tasks/2025-i-7-p6.png","generated/tasks/2025-ii-10-p4.png","generated/tasks/2025-ii-11-p5.png","generated/tasks/2025-ii-12-p6.png","generated/tasks/2025-ii-8-p2.png","generated/tasks/2025-ii-9-p3.png","pdfs/2021-hindamisjuhend.pdf","pdfs/2021-laia-i.pdf","pdfs/2021-laia-ii.pdf","pdfs/2022-hindamisjuhend.pdf","pdfs/2022-laia-i.pdf","pdfs/2022-laia-ii.pdf","pdfs/2023-hindamisjuhend.pdf","pdfs/2023-laia-i.pdf","pdfs/2023-laia-ii.pdf","pdfs/2024-hindamisjuhend.pdf","pdfs/2024-laia-i.pdf","pdfs/2024-laia-ii.pdf","pdfs/2025-hindamisjuhend.pdf","pdfs/2025-laia-i.pdf","pdfs/2025-laia-ii.pdf"]),
	mimeTypes: {".json":"application/json",".png":"image/png",".html":"text/html",".pdf":"application/pdf"},
	_: {
		client: {start:"_app/immutable/entry/start.DS3Vcdpy.js",app:"_app/immutable/entry/app.DKolQ9-A.js",imports:["_app/immutable/entry/start.DS3Vcdpy.js","_app/immutable/chunks/BsaYw57T.js","_app/immutable/chunks/C3V6Csdy.js","_app/immutable/entry/app.DKolQ9-A.js","_app/immutable/chunks/C3V6Csdy.js","_app/immutable/chunks/Dj6f-nJM.js","_app/immutable/chunks/DEDqjojZ.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
