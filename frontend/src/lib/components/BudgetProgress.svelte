<script lang="ts">
	import type { Budget } from '$lib/types';
	import { formatRupiah } from '$lib/format';

	let { budgets }: { budgets: Budget[] } = $props();

	function barClass(b: Budget): string {
		if (b.usage_percent >= 100) return 'over';
		if (b.usage_percent >= 80) return 'warn';
		return '';
	}
</script>

{#if budgets.length === 0}
	<div class="empty">No budgets set for this month.</div>
{:else}
	{#each budgets as b (b.id)}
		<div style="margin-bottom: 14px">
			<div class="row" style="justify-content: space-between; margin-bottom: 5px">
				<strong style="font-size: 13px">{b.category_name}</strong>
				<span class="muted" style="font-size: 12px">
					{formatRupiah(b.spent)} / {formatRupiah(b.amount)}
				</span>
			</div>
			<div class="progress">
				<div class={barClass(b)} style="width: {Math.min(100, b.usage_percent)}%"></div>
			</div>
			<div class="muted" style="font-size: 11px; margin-top: 3px">
				{b.usage_percent}% used ·
				{#if b.remaining >= 0}
					{formatRupiah(b.remaining)} remaining
				{:else}
					{formatRupiah(-b.remaining)} over budget
				{/if}
			</div>
		</div>
	{/each}
{/if}
