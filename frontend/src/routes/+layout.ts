export const ssr = false;

import { auth } from '$lib/stores/auth.svelte';

export async function load() {
	await auth.init();
}
