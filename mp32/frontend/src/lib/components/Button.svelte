
<script lang="ts">
    import type { Snippet } from 'svelte';

    let { children }: { children: Snippet } = $props();
</script>

<button type="button" class="btn text-xs bg-surface-500 text-surface-100 rounded-xl hover:text-black hover:bg-yellowbrand">
    {@render children()}
</button>
