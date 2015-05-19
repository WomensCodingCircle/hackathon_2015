$(document).ready(function(){
$('#label_search').magicSuggest({
			name: 'neurons',
			data: neuron_names,
			width:100
		});
$('#label_search').css('width','200px');
});
