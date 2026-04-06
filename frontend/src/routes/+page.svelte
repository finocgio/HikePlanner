<script>
    import { browser, dev } from "$app/environment";
    import { onMount } from "svelte";

    let url = dev ? "http://localhost:5000" : "";
    if (!dev && browser) {
        url = location.protocol + "//" + location.host;
    }

    let downhill = 300;
    let uphill = 700;
    let length = 10000;

    let prediction = "n.a.";
    let linearPrediction = "n.a.";
    let din33466 = "n.a.";
    let sac = "n.a.";

    let similarHikes = []; //finocgio Erweiterung

    let debounceId;

    async function predict() {
        let result = await fetch(
            url +
                "/api/predict?" +
                new URLSearchParams({
                    downhill: downhill,
                    uphill: uphill,
                    length: length,
                }),
            {
                method: "GET",
            },
        );
        let data = await result.json();
        console.log(data);
        prediction = data.time;
        linearPrediction = data.linear;
        din33466 = data.din33466;
        sac = data.sac;
        similarHikes = data.similar_hikes ?? []; //finocgio Erweiterung
    }

    onMount(() => {
        predict();
    });

    function schedulePredict() {
        if (debounceId) {
            clearTimeout(debounceId);
        }
        debounceId = setTimeout(() => {
            predict();
        }, 300);
    }
</script>

<svelte:head>
    <title>HikePlanner</title>
</svelte:head>

<div class="app-bg">
    <main class="container py-5">
        <div class="row g-4 align-items-start align-items-lg-stretch">
            <div class="col-lg-6">
                <div class="p-4 p-lg-5 bg-white shadow-sm rounded-4 h-100">
                    <h1 class="display-6 fw-bold mb-2">HikePlanner</h1>
                    <p class="text-muted mb-4">
                        Schätze die Gehzeit basierend auf Distanz und Höhenmetern.
                    </p>

                    <form class="vstack gap-3" on:submit|preventDefault={predict}>
                        <div>
                            <label for="downhill" class="form-label fw-semibold">Abwärts [m]</label>
                            <div class="row g-2 align-items-center">
                                <div class="col-4">
                                    <input
                                        id="downhill"
                                        type="number"
                                        class="form-control"
                                        bind:value={downhill}
                                        min="0"
                                        max="10000"
                                        on:input={schedulePredict}
                                    />
                                </div>
                                <div class="col-8">
                                    <input
                                        type="range"
                                        class="form-range"
                                        bind:value={downhill}
                                        min="0"
                                        max="10000"
                                        step="10"
                                        on:input={schedulePredict}
                                    />
                                </div>
                            </div>
                        </div>

                        <div>
                            <label for="uphill" class="form-label fw-semibold">Aufwärts [m]</label>
                            <div class="row g-2 align-items-center">
                                <div class="col-4">
                                    <input
                                        id="uphill"
                                        type="number"
                                        class="form-control"
                                        bind:value={uphill}
                                        min="0"
                                        max="10000"
                                        on:input={schedulePredict}
                                    />
                                </div>
                                <div class="col-8">
                                    <input
                                        type="range"
                                        class="form-range"
                                        bind:value={uphill}
                                        min="0"
                                        max="10000"
                                        step="10"
                                        on:input={schedulePredict}
                                    />
                                </div>
                            </div>
                        </div>

                        <div>
                            <label for="length" class="form-label fw-semibold">Distanz [m]</label>
                            <div class="row g-2 align-items-center">
                                <div class="col-4">
                                    <input
                                        id="length"
                                        type="number"
                                        class="form-control"
                                        bind:value={length}
                                        min="0"
                                        max="30000"
                                        on:input={schedulePredict}
                                    />
                                </div>
                                <div class="col-8">
                                    <input
                                        type="range"
                                        class="form-range"
                                        bind:value={length}
                                        min="0"
                                        max="30000"
                                        step="10"
                                        on:input={schedulePredict}
                                    />
                                </div>
                            </div>
                        </div>

                        <div class="d-grid">
                            <button class="btn btn-primary btn-lg" type="submit">
                                Zeit vorhersagen
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div class="col-lg-6">
                <div class="p-4 p-lg-5 bg-white shadow-sm rounded-4 h-100">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <h2 class="h5 mb-0 fw-semibold">Dauer</h2>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-sm align-middle">
                            <tbody>
                                <tr>
                                    <th scope="row" class="text-muted">Model (Gradient Boosting Regressor)</th>
                                    <td class="fw-semibold">{prediction}</td>
                                </tr>
                                <tr>
                                    <th scope="row" class="text-muted">Model (Linear Regression)</th>
                                    <td class="fw-semibold">{linearPrediction}</td>
                                </tr>
                                <tr>
                                    <th scope="row" class="text-muted">DIN33466</th>
                                    <td class="fw-semibold">{din33466}</td>
                                </tr>
                                <tr>
                                    <th scope="row" class="text-muted">SAC</th>
                                    <td class="fw-semibold">{sac}</td>
                                </tr>
                                <!-- finocgio Erweiterung von hier -->
                            <hr class="my-4" />

<div class="d-flex align-items-center justify-content-between mb-3">
    <h2 class="h5 mb-0 fw-semibold">Ähnliche Wanderungen</h2>
</div>

{#if similarHikes.length === 0}
    <p class="text-muted mb-0">Keine ähnlichen Wanderungen gefunden.</p>
{:else}
    <div class="table-responsive">
        <table class="table table-sm align-middle">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Distanz</th>
                    <th>Aufstieg</th>
                    <th>Abstieg</th>
                    <th>Dauer</th>
                </tr>
            </thead>
            <tbody>
                {#each similarHikes as hike}
                    <tr>
                        <td>{hike.title}</td>
                        <td>{hike.length_3d} m</td>
                        <td>{hike.uphill} hm</td>
                        <td>{hike.downhill} hm</td>
                        <td>{hike.moving_time}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
{/if}
                                <!--finocgio Erweiterung bis hier -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>
