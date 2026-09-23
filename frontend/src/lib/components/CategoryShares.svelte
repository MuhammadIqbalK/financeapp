<script lang="ts">
	import type { CategoryShare } from '$lib/types';
	import { formatRupiah } from '$lib/format';

	let { shares }: { shares: CategoryShare[] } = $props();

	const PALETTE = ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#be185d', '#65a30d'];
</script>

{#if shares.length === 0}
	<div class="empty">No expenses in this period.</div>
{:else}
	{#each shares as s, i (s.category_id)}
		<div class="share-row">
			<span class="name">{s.category_name}</span>
			<span class="bar">
				<div class="progress">
					<div
						style="width: {s.percent}%; background: {PALETTE[i % PALETTE.length]}"
					></div>
				</div>
			</span>
			<span class="pct">{s.percent}%</span>
		</div>
		<div class="muted" style="font-size: 11px; margin: -4px 0 8px 120px">
			{formatRupiah(s.amount)}
		</div>
	{/each}
{/if}
