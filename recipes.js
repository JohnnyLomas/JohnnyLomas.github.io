function postRecipe(){
	//TODO: This function needs to take
	//      the information provide in the
	//      html form tag and the recipe
	//      to the recipe dataset...
	
}

function renderRecipeBody(){
	//TODO: This function needs to build the 
	//      main body of the webpage with card
	//      list recipes given a recipe object.
	//      Should accept any filtered variation
	//      of the recipe object.
	for (let i = 0;i < recipeObj.length;i++){
		`<div class="carditem">
			<div class="recipeimage">
				<img src="${recipeObj[i].imageURL}">
			</div>
			<div class="recipecomments">
				<p>${recipeObj.comments}</p>
			</div
			<button class="viewbtn">View Recipe</button>
	 	</div>` 
	 }
}