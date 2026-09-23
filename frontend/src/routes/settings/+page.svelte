<script lang="ts">
	import { authApi } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';

	let email = $state('');
	let currentPassword = $state('');
	let newPassword = $state('');
	let msg = $state('');
	let err = $state('');
	let busy = $state(false);

	$effect(() => {
		if (auth.user && !email) email = auth.user.email;
	});

	async function saveEmail() {
		msg = '';
		err = '';
		busy = true;
		try {
			const user = await authApi.updateMe({ email });
			auth.user = user;
			msg = 'Email updated.';
		} catch (e) {
			err = e instanceof Error ? e.message : 'Failed';
		} finally {
			busy = false;
		}
	}

	async function savePassword() {
		msg = '';
		err = '';
		busy = true;
		try {
			await authApi.updateMe({ current_password: currentPassword, new_password: newPassword });
			currentPassword = '';
			newPassword = '';
			msg = 'Password updated.';
		} catch (e) {
			err = e instanceof Error ? e.message : 'Failed';
		} finally {
			busy = false;
		}
	}

	function logout() {
		auth.logout();
		goto('/login');
	}
</script>

<div class="page-head">
	<h1>Settings</h1>
</div>

{#if msg}<div class="muted" style="color: var(--green); margin-bottom: 10px">{msg}</div>{/if}
{#if err}<div class="error">{err}</div>{/if}

<div class="grid grid-2">
	<div class="card">
		<h2>Profile</h2>
		<div class="field">
			<label for="s-email">Email</label>
			<input id="s-email" type="email" bind:value={email} />
		</div>
		<button class="primary" onclick={saveEmail} disabled={busy}>Save Email</button>
	</div>

	<div class="card">
		<h2>Change Password</h2>
		<div class="field">
			<label for="s-current">Current Password</label>
			<input id="s-current" type="password" bind:value={currentPassword} />
		</div>
		<div class="field">
			<label for="s-new">New Password</label>
			<input id="s-new" type="password" minlength="6" bind:value={newPassword} />
		</div>
		<button class="primary" onclick={savePassword} disabled={busy}>Update Password</button>
	</div>
</div>

<div class="card" style="margin-top: 14px">
	<h2>Session</h2>
	<p class="muted">Signed in as {auth.user?.email ?? '—'}</p>
	<button class="danger" onclick={logout}>Logout</button>
</div>
