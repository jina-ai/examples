
var contact_form = new Vue({
	el: '#app', // id of the 'app'
	data: {
		search_to_word: '',   // data for the name on the form
		items: []
	},
	methods: { // all the actions our app can do
		submitForm: function () {
			console.log('submitting message...');
			var xhr = new XMLHttpRequest();
			var url = "http://localhost:65481/api/search";
			xhr.open("POST",url,true);
			xhr.setRequestHeader("Content-type", "application/json");
			xhr.onreadystatechange = function (vm) {
				if (xhr.readyState == 4 && xhr.status == 200) {
					var json = JSON.parse(xhr.responseText);
					var my_grid_data = [];
					for (var searched_words of json.search.docs) {
						for (var match of searched_words.matches) {
							if ('chunks' in match) {
								title_ = match.text;
								score_  = match.score.value;
								my_grid_data.push({score: score_, title: title_});
							} 
						}
					}
					vm.items = my_grid_data;
					console.log(json);
				}
			}.bind(xhr,this);
			var data = JSON.stringify({"top_k": 10, "mode": "search", "data": ["text:"+this.search_to_word]});
			/*clear form */
			this.search_to_word = '';
			xhr.send(data);
		}

	},
});
