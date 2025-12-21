<script lang="ts">
	import SplitPanel from './SplitPanel.svelte';
	import { leftPanel, rightPanel } from '$lib/stores/editor.svelte';
</script>

<div class="grid h-full w-full grid-cols-2">
	<div class="h-full border-r-2 border-border">
		<SplitPanel panel={leftPanel} panelId="left" />
	</div>
	<div class="h-full">
		<SplitPanel panel={rightPanel} panelId="right" />
	</div>
</div>
