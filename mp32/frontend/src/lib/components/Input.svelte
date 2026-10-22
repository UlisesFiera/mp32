
<script lang="ts">
    import type { HTMLInputAttributes } from 'svelte/elements';
    let {
        id = '',
        type = '',
        autocomplete = 'off',
    }: {
        id?: string;
        type?: string;
        autocomplete?: HTMLInputAttributes['autocomplete'];
    } = $props();
</script>

<input class="input text-xs rounded-xl bg-surface-500 ring-0" id={id} type={type} autocomplete={autocomplete}>
