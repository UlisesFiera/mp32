
<script lang="ts">
    import type { Snippet } from 'svelte';

    let { children }: { children: Snippet } = $props();
</script>

<div class="z-10 flex flex-col w-fit items-center justify-center gap-4 p-7 
    rounded-xl bg-transparent backdrop-blur-xs border-1 border-white/20">
    {@render children()}
</div>
