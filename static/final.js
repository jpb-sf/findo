console.log(window.innerWidth)

let toggleStatus = false;
	
let toggle = function() {
	let greeting = document.querySelector('.nav__greeting--wrapper');
	let menu = document.querySelector('.nav__mobilemenu--wrapper');
	let linksArray = document.querySelectorAll('.nav__mobilemenu--wrapper a');
	let bulletArray = document.querySelectorAll('.nav__mobilemenu--wrapper li');
	let rule = document.querySelector('.rule__mobilemenu');
	let signout = document.querySelector('.nav__mobilemenu--wrapper h5');
	let header = document.querySelector('.nav__header');

	let linksLen = linksArray.length;
	let bulLen = bulletArray.length;
	
	if (toggleStatus === false)
	{	
		// header.style.visibility = "hidden";
		greeting.style.height = "2.8rem"
		menu.style.visibility = "visible";
		menu.style.width = "100%";
		menu.style.height = "21rem";
		rule.style.opacity = "1";
		signout.style.opacity = "1";
		header.style.visibility = "hidden"
		
		for (let i = 0; i < linksLen; i++)
		{
			linksArray[i].style.opacity = "1";
			linksArray[i].style.visibility ="visible";
		}

		for (let i = 0; i < bulLen; i++)
		{
			bulletArray[i].style.opacity = "1";
		}
		
		toggleStatus = true;
		
	} else {
		greeting.style.height = "4.8rem"
		menu.style.visibility = "hidden";
		menu.style.width = "0rem";
		menu.style.height = "0rem";
		rule.style.opacity = "0";
		signout.style.opacity = "0";
		header.style.visibility = "visible"


		for (let i = 0; i < linksLen; i++)
		{
			linksArray[i].style.opacity = "0";
			linksArray[i].style.visibility ="hidden";
		}

		for (let i = 0; i < bulLen; i++) {
			bulletArray[i].style.opacity = "0";
		}
		
		toggleStatus = false;
	}
}


// Function gathers updated input and makes post request to server to input edited data in the db
function edit(itemid)
{
	let itemId, location, comments, category, categoryName;
	category = document.querySelector('#category').value
	itemId = itemid;        
	// description = document.querySelector('#description').value;
	location = document.querySelector('#location').value;
	comments = document.querySelector('#comments').value;

	if (category == "")
	{
		let error = document.querySelector('.no_category');
		error.innerHTML = "Please select a category";
	}
	else
	{	
		// Send post request
		const xhttp = new XMLHttpRequest();
		
		// when ready
		xhttp.onreadystatechange = function()
		{	
			data = xhttp.responseText;
			if (xhttp.readyState == 4 && xhttp.status == 200)
			{	
				if (data == "True")
				{
					return window.location = '/category/' + category	
				}
				else if (data == "False")
				{
					return window.location = '/'
				}
			}
		}
	
		let data = {category: category, itemId: itemId, location: location, comments: comments};
		
		let send = JSON.stringify(data);
		console.log(send)
		xhttp.open("post", "/change");
		xhttp.setRequestHeader('Content-Type', 'application/json');
		xhttp.send(send);
	}
}


// Function for username registration validation
function check(value) 
{	
	let test = document.querySelector('.test');

	if (value == "")
	{
		test.innerHTML = "";
		return false;
	}

	else if (value.length < 3 && !value.length == 0)
	{	
		var delayInMilliseconds = 1000;
		setTimeout(function() {
			test.style.display = "block";
			test.innerHTML = "Must be at least 3 characters";
			test.setAttribute("class", "test gray");
		}, delayInMilliseconds);
	}
	else 
	{
		let params = "username" + "=" + value;
		const xhttp = new XMLHttpRequest();

		// Send paramaters to server function 'check'
		xhttp.open("get", "/check" + "?" + params, true);
		// xhttp.setRequestHeader('Content-Type', 'text/plain');
		
		xhttp.onreadystatechange = function()
		{
			if (xhttp.readyState == 4 && xhttp.status == 200)
			{	
				let data;
				data = JSON.parse(xhttp.responseText);
				// test  = document.querySelector('.test');

				// If username is taken
				if (data == false)
				{	
					test.style.display = "block";
					test.innerHTML = "Username already taken";
					test.setAttribute("class", "test red");
					return false;
				}

				// If username is not taken
				else if (data == true)
				{	
					test.style.display = "block";
					test.innerHTML = "Username is available";
					test.setAttribute("class", "test green");
					return true;
				}
			}
		}
		xhttp.send(null);
	}
}

// // Prevent Registration form from submitting if...
document.querySelector("#reg_form").addEventListener("submit", function(event)
{	
	let password, confirmation, user, test2;
	password  = document.querySelector('.password');
	confirmation = document.querySelector('.confirmation');
	user = document.querySelector('.username');
	test2 = document.querySelector('.test2');

	// If username is less than 3 characters, prevent submit
	if (user.value.length < 3) 
	{
		event.preventDefault();
		return false;
	}

	// If password is less than 3 characters, prevent submit
	if (password.value.length < 3)
	{
		event.preventDefault();
		test2.innerHTML = "Password must be at least 3 characters";
		test2.setAttribute("class", "test2 red");

		return false;
	} else {
		test2.innerHTML = "";
	}

	// If password and confirmation don't match, prevent submit
	if (password.value != confirmation.value)
	{
		event.preventDefault();
		let test3 = document.querySelector('.test3');
		test3.innerHTML = "Passwords don't match";
		test3.setAttribute("class", "test3 red");
		return false;
	}	
});

// Function receives category value, makes a Get request, generates new categorgy page
function display(value)
{	
	return window.location = '/category/' + value;
    		
}


// Modify function determines if edit, or delete request, and routes accordingly.
function modify(itemId, action)
{	
	// Get request function and handler
	let makeRequest = function()
	{
		// Create params to pass in with Get request
		let param = "itemId" + "=" + itemId;
		let param2 = "action" + "=" + action

		const xhttp = new XMLHttpRequest();

		xhttp.open("get", "/modify" + "?" + param + "&" + param2)

		// When ready
		xhttp.onreadystatechange = function()
		{
			if (xhttp.readyState == 4 && xhttp.status == 200)
			{ 
				let data = xhttp.responseText;
				// If action is delete, and item is correctly deleted, backend will return True.
				if (data == "True")
				{	
					return document.location.reload();
				}
				
				else if (data == "False")
	    		{
	    			return window.location = '/login'
	    		}
	    		// Else, if action is edit, and backend confirms user owns it
	    		// item id is returned and user is rerouted to correct edit page/form
	    		else
	    		{
	    			return window.location = '/edit/' + data
	    		}
			}

		}
		xhttp.send(null)
	}
	
	if (action == "delete")
	{
		if (window.confirm("You are about to delete this entry. Continue?"))
		{	
			return makeRequest();
	
		} else {
			return false
		}
	}
	
	else if (action == "edit")
	{	
		return makeRequest();
	
	} else {
		return false
	}
}






