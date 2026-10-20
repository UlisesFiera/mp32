<script lang="ts">
    import { ArrowUpRight } from 'lucide-svelte';
</script>

<div class="min-h-screen flex items-center justify-center">
    <div class="flex flex-col w-fit items-center justify-center gap-8 border p-5 rounded-lg border-brand">
        <form class="w-64 space-y-4">
            <fieldset class="space-y-2">
                <legend>Login</legend>

                <label class="flex flex-col gap-2 text-xs">
                    <span>User</span>
                    <input class="input" type="email" />
                </label>

                <label class="flex flex-col gap-2 text-xs">
                    <span>Password</span>
                    <input class="input" type="password" />
                </label>
            </fieldset>
        </form>

        <div class="flex items-center gap-4">
            <button type="button" class="btn preset-filled">
                <span>log-in</span>
            </button>
            <button type="button" class="btn preset-filled">
                <span>sign-up</span>
                <ArrowUpRight size={16} />
            </button>
        </div>
    </div>
</div>