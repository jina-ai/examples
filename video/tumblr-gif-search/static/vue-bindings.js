var VueMasonryPlugin = window["vue-masonry-plugin"].VueMasonryPlugin;
Vue.use(VueMasonryPlugin);

const vm = new Vue({
    el: '#jina-ui',
    data: {
        serverUrl: './model/',
        modelId: '20200416085013',//'20191122144241',
        databasePath: '/topk.json',
        results: [],
        queryItem: null,
        docItem: null,
        loadedItem: 0,
        loadedQuery: 0,
        jsonTreeLevel: 3
    },
    mounted: function () {
        this.$nextTick(function () {
            this.refreshDatabase();
        })
    },

    computed: {
        databaseUrl: function () {
            return this.serverUrl + this.modelId + this.databasePath
        }
    },
    methods: {
        syntaxHighlight: function (json) {
            if (typeof json != 'string') {
                json = JSON.stringify(json, undefined, 2);
            }
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                var cls = 'number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'key';
                    } else {
                        cls = 'string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'boolean';
                } else if (/null/.test(match)) {
                    cls = 'null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        },
        getGifName: function (item) {
            var t = item.split('/');
            return t[t.length - 1];
        },
        getThumbnail: function (item) {
            return vm.serverUrl + vm.modelId + '/thumbnail/' + vm.getGifName(item) + '.jpg';
        },
        setQueryItem: function (item) {
            // kill all image request before change query term
            // doesnt work on firefox, will freeze all gif
            // window.stop();
            vm.loadedItem = 0;
            vm.queryItem = item;
            vm.$redrawVueMasonry('my-masonry');
        },
        addLoadedImage: function () {
            vm.loadedItem += 1;
            if (vm.loadedItem === vm.queryItem.topkResults.length) {
                vm.$redrawVueMasonry('my-masonry');
            }
        },
        addLoadedQuery: function () {
            vm.loadedQuery += 1;
        },
        setDocItem: function (item) {
            vm.docItem = item;
            vm.jsonTreeLevel = 3;
        },
        refreshDatabase: function () {
            $.ajax({
                url: this.databaseUrl,
                dataType: 'text',
                cache: false,
                beforeSend: function () {
                    console.log("Loading");
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log(jqXHR);
                    console.log(textStatus);
                    console.log(errorThrown);
                },
                success: function (data) {
                    console.log('Success');
                    data.trim().split('\n').forEach(function (value) {
                        if (value.trim().length > 0) {
                            var v = JSON.parse(value);
                            vm.results.push(v);
                        }
                    })
                },
                complete: function () {
                    console.log('Finished all tasks, load ' + vm.results.length + ' items');
                    vm.queryItem = vm.results[0];
                    vm.docItem = vm.results[0].topkResults[0]
                }
            });
        }
    }

});