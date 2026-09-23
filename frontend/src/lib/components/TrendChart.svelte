<script lang="ts">
	import type { Point } from '$lib/types';
	import { formatCompact } from '$lib/format';

	let { points }: { points: Point[] } = $props();

	const W = 640;
	const H = 180;
	const PAD = { top: 10, right: 8, bottom: 22, left: 44 };

	const max = $derived(Math.max(1, ...points.map((p) => Math.max(p.income, p.expense))));
	const chartW = W - PAD.left - PAD.right;
	const chartH = H - PAD.top - PAD.bottom;
	const groupW = $derived(points.length ? chartW / points.length : chartW);
	const barW = $derived(Math.max(2, Math.min(14, groupW / 2.5)));

	const gridLines = $derived([0, 0.25, 0.5, 0.75, 1].map((f) => ({ f, v: max * f })));

	function y(v: number): number {
		return PAD.top + chartH - (v / max) * chartH;
	}
</script>

<div>
	<svg viewBox="0 0 {W} {H}" style="width: 100%; height: auto" role="img" aria-label="Income vs expense chart">
		{#each gridLines as g (g.f)}
			<line
				x1={PAD.left}
				x2={W - PAD.right}
				y1={y(g.v)}
				y2={y(g.v)}
				stroke="#eef0f3"
				stroke-width="1"
			/>
			<text x={PAD.left - 6} y={y(g.v) + 3} text-anchor="end" font-size="9" fill="#9ca3af">
				{formatCompact(g.v)}
			</text>
		{/each}

		{#each points as p, i (p.label)}
			{@const x = PAD.left + i * groupW + groupW / 2}
			<rect
				x={x - barW - 1}
				y={y(p.income)}
				width={barW}
				height={Math.max(0, PAD.top + chartH - y(p.income))}
				fill="#16a34a"
				rx="2"
			>
				<title>{p.label}: +{formatCompact(p.income)}</title>
			</rect>
			<rect
				x={x + 1}
				y={y(p.expense)}
				width={barW}
				height={Math.max(0, PAD.top + chartH - y(p.expense))}
				fill="#dc2626"
				rx="2"
			>
				<title>{p.label}: -{formatCompact(p.expense)}</title>
			</rect>
		{/each}

		{#if points.length > 0}
			{@const every = Math.max(1, Math.ceil(points.length / 8))}
			{#each points as p, i (p.label)}
				{#if i % every === 0}
					<text
						x={PAD.left + i * groupW + groupW / 2}
						y={H - 6}
						text-anchor="middle"
						font-size="9"
						fill="#9ca3af"
					>
						{p.label.slice(5)}
					</text>
				{/if}
			{/each}
		{/if}
	</svg>
	<div class="chart-legend">
		<span><span class="dot" style="background:#16a34a"></span>Income</span>
		<span><span class="dot" style="background:#dc2626"></span>Expense</span>
	</div>
</div>
