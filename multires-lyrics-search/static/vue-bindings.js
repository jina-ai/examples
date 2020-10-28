var VueMasonryPlugin = window["vue-masonry-plugin"].VueMasonryPlugin;
Vue.use(VueMasonryPlugin);

const vm = new Vue({
    el: '#jina-ui',
    data: {
        serverUrl: 'http://localhost:65481/api/search',
        top_k: 50,
        topkDocs: [],
        topkDocsDict: {},
        results: [],
        searchQuery: '',
        queryChunks: [],
        selectQueryChunks: [],
        queryItem: [],
        docItem: null,
        loadedItem: 0,
        loadedQuery: 0,
        searchQueryIsDirty: false,
        isCalculating: false,
        distThreshold: 999,
        sliderOptions: {
            dotSize: 14,
            width: 'auto',
            height: 4,
            contained: false,
            direction: 'ltr',
            data: null,
            min: 999,
            max: 0,
            interval: 0.01,
            disabled: false,
            clickable: true,
            duration: 0.5,
            adsorb: false,
            lazy: false,
            tooltip: 'active',
            tooltipPlacement: 'top',
            tooltipFormatter: void 0,
            useKeyboard: false,
            keydownHook: null,
            dragOnClick: false,
            enableCross: true,
            fixed: false,
            minRange: void 0,
            maxRange: void 0,
            order: true,
            marks: false,
            dotOptions: void 0,
            process: true,
            dotStyle: void 0,
            railStyle: void 0,
            processStyle: void 0,
            tooltipStyle: void 0,
            stepStyle: void 0,
            stepActiveStyle: void 0,
            labelStyle: void 0,
            labelActiveStyle: void 0,
        }
    },
    mounted: function () {

    },
    components: {
        'vueSlider': window['vue-slider-component'],
    },
    computed: {
        searchIndicator: function () {
            if (this.isCalculating) {
                return '⟳ Fetching new results...'
            } else if (this.searchQueryIsDirty) {
                return '... Typing'
            } else {

                return '✓ Done'
            }
        }
    },
    watch: {
        searchQuery: function () {
            this.searchQueryIsDirty = true
            this.expensiveOperation()
        },
        distThreshold: function () {
            this.refreshAllCards();
        }
    },
    methods: {
        clearAllSelect: function () {
            vm.queryChunks.forEach(function (item, i) {
                item['isSelect'] = !item['isSelect'];
                vm.refreshAllCards();
            });
        },
        selectChunk: function (item) {
            item['isSelect'] = !item['isSelect'];
            vm.refreshAllCards();
        },
        refreshAllCards: function () {
            vm.topkDocsDict = new Map(vm.topkDocs.map(i => [i.id, {
                'text': i.text,
                'hlchunk': [],
                'renderHTML': i.text
            }]));
            vm.queryChunks.forEach(function (item, i) {
                if (!('isSelect' in item)) {
                    item['isSelect'] = true;
                }
                if (item['isSelect']) {
                    item.matches.forEach(function (r) {
                        if (vm.topkDocsDict.has(r.parentId)) {
                            if (r.score.value < vm.distThreshold) {
                                // console.log(item)
                                vm.topkDocsDict.get(r.parentId)['hlchunk'].push({
                                    'range': r.location,
                                    'idx': i,
                                    'dist': r.score.value,
                                    'range_str': r.location[0] + ',' + r.location[1]
                                });
                            }
                            if (r.score.value < vm.sliderOptions.min) {
                                vm.sliderOptions.min = r.score.value.toFixed(2)
                            }
                            if (r.score.value > vm.sliderOptions.max) {
                                vm.sliderOptions.max = r.score.value.toFixed(2)
                            }
                        } else {
                            console.error(r.id);
                        }
                    });
                }
            });
            vm.topkDocsDict.forEach(function (value, key, map) {
                vm.topkDocsDict.get(key)['hlchunk'].sort(function (a, b) {
                    return b['range'][0] - a['range'][0]
                })
                var replace_map = new Map();
                value['hlchunk'].forEach(function (item) {
                    if (!replace_map.has(item['range_str'])) {
                        replace_map.set(item['range_str'], [])
                    }
                    replace_map.get(item['range_str']).push(item)

                })

                replace_map.forEach(function (item, kk, mm) {
                    value['renderHTML'] = replaceRange(value['renderHTML'], item[0]['range'][0], item[0]['range'][1], item)
                })
            })
            vm.$nextTick(function () {
                vm.$redrawVueMasonry('my-masonry');
            })
        },
        // This is where the debounce actually belongs.
        expensiveOperation: _.debounce(function () {
            this.isCalculating = true
            vm.selectQueryChunks.length = 0;
            $.ajax({
                url: this.serverUrl,
                type: "POST",
                contentType: "application/json; charset=utf-8",
                cache: false,
                data: JSON.stringify({
                    "top_k": this.top_k,
                    "data": [this.searchQuery]
                }),
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log(jqXHR);
                    console.log(textStatus);
                    console.log(errorThrown);
                },
                success: function (data) {
                    vm.topkDocs = data.search.docs[0].matches;
                    vm.queryChunks = data.search.docs[0].chunks;
                    vm.refreshAllCards();
                    console.log('Success');
                },
                complete: function () {
                    vm.isCalculating = false
                    vm.searchQueryIsDirty = false
                    vm.$nextTick(function () {
                        vm.$redrawVueMasonry('my-masonry');
                    })
                }
            });

        }, 500)
    }
});

function replaceRange(s, start, end, chunks) {
    var content = s.substring(start, end)
    chunks.forEach(function (c) {
        content = "<span class=\"match-chunk query-chunk match-chunk-" + c.idx + "\" match-dist=" + c.dist + " style=\"background:" + selectColor(c.idx, true) + "\">" + content + "</span>"
    })
    return s.substring(0, start) + content + s.substring(end);
}

function selectColor(number, colored) {
    if (!colored) {
        return `#fff`;
    }
    const hue = number * 137.508; // use golden angle approximation
    return `hsl(${hue},50%,75%)`;
}
