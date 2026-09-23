<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		title,
		onclose,
		children
	}: { title: string; onclose: () => void; children: Snippet } = $props();

	function onkeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onclose();
	}
</script>

<svelte:window {onkeydown} />

<div
	class="modal-backdrop"
	role="presentation"
	onclick={(e) => {
		if (e.target === e.currentTarget) onclose();
	}}
>
	<div class="modal" role="dialog" aria-modal="true" aria-label={title}>
		<div class="modal-head">
			<h2>{title}</h2>
			<button class="ghost" onclick={onclose} aria-label="Close">✕</button>
		</div>
		{@render children()}
	</div>
</div>
