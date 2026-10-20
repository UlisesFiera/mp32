<script lang="ts">
    import { ArrowUpRight } from 'lucide-svelte';
</script>

<div class="min-h-screen flex items-center justify-center">
    <div class="z-1 flex flex-col w-fit items-center justify-center gap-4 p-7 rounded-lg bg-surface-500">
        <form class="w-64 space-y-4">
            <fieldset class="space-y-2 text-surface-100">
                <legend>Login</legend>

                <label class="flex flex-col text-xs">
                    <span>User</span>
                    <input class="input text-xs" type="email" />
                </label>

                <label class="flex flex-col text-xs">
                    <span>Password</span>
                    <input class="input text-xs" type="password" />
                </label>
            </fieldset>
        </form>

        <div class="flex items-center gap-4">
            <button type="button" class="btn preset-filled text-xs bg-surface-800 text-surface-100">
                <span>log-in</span>
            </button>
            <button type="button" class="btn preset-filled text-xs bg-surface-800 text-surface-100">
                <span>sign-up</span>
                <ArrowUpRight size={16} />
            </button>
        </div>
    </div>
</div>