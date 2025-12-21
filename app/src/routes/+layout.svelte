<script lang="ts">
	import '../app.css';
	import ToastContainer from '$lib/components/ui/ToastContainer.svelte';
	import LoadingOverlay from '$lib/components/ui/LoadingOverlay.svelte';

	let { children } = $props();
</script>

<div class="h-screen w-screen overflow-hidden bg-bg-primary">
	{@render children()}
</div>

<ToastContainer />
<LoadingOverlay />
