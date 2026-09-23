<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth.svelte';

	let { children } = $props();

	const NAV = [
		{ href: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
		{ href: '/transactions', label: 'Transactions', icon: 'transactions' },
		{ href: '/accounts', label: 'Accounts', icon: 'accounts' },
		{ href: '/categories', label: 'Categories', icon: 'categories' },
		{ href: '/budgets', label: 'Budgets', icon: 'budgets' },
		{ href: '/settings', label: 'Settings', icon: 'settings' }
	] as const;

	const ICONS: Record<string, string> = {
		dashboard:
			'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
		transactions:
			'<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
		accounts:
			'<path d="M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/><path d="M16 7V5a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v2"/><circle cx="16.5" cy="14" r="1.2"/>',
		categories:
			'<path d="M20.59 13.41 12 22 2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82Z"/><circle cx="7" cy="7" r="1.2"/>',
		budgets:
			'<line x1="6" y1="20" x2="6" y2="16"/><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/>',
		settings:
			'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>',
		menu: '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>'
	};

	const stored = localStorage.getItem('sidebar-collapsed');
	let collapsed = $state(stored !== null ? stored === '1' : window.innerWidth < 900);

	$effect(() => {
		localStorage.setItem('sidebar-collapsed', collapsed ? '1' : '0');
	});

	$effect(() => {
		if (!auth.ready) return;
		const path = page.url.pathname;
		if (!auth.isAuthenticated && path !== '/login') {
			goto('/login');
		} else if (auth.isAuthenticated && path === '/login') {
			goto('/dashboard');
		} else if (auth.isAuthenticated && path === '/') {
			goto('/dashboard');
		} else if (!auth.isAuthenticated && path === '/') {
			goto('/login');
		}
	});

	function isActive(href: string): boolean {
		return page.url.pathname.startsWith(href);
	}
</script>

{#if !auth.ready}
	<div class="empty" style="padding-top: 20vh">Loading…</div>
{:else if !auth.isAuthenticated || page.url.pathname === '/login'}
	{@render children()}
{:else}
	<div class="layout" class:is-collapsed={collapsed}>
		<aside class="sidebar">
			<div class="top">
				<div class="brand"><span class="brand-text">Personal Finance</span></div>
				<button
					class="toggle"
					onclick={() => (collapsed = !collapsed)}
					aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
					aria-expanded={!collapsed}
					title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
				>
					<svg viewBox="0 0 24 24" aria-hidden="true">{@html ICONS.menu}</svg>
				</button>
			</div>
			<nav>
				{#each NAV as item (item.href)}
					<a href={item.href} class:active={isActive(item.href)} title={item.label}>
						<svg viewBox="0 0 24 24" aria-hidden="true">{@html ICONS[item.icon]}</svg>
						<span class="label">{item.label}</span>
					</a>
				{/each}
			</nav>
			<div class="foot">
				<div class="label">{auth.user?.email ?? ''}</div>
				<div style="margin-top: 6px" class="label">
					<button
						class="small"
						onclick={() => {
							auth.logout();
							goto('/login');
						}}
					>
						Logout
					</button>
				</div>
			</div>
		</aside>
		<main class="main">
			{@render children()}
		</main>
	</div>
{/if}
