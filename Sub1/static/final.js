console.log(window.innerWidth)

// Script in one and only script for the findo app.
// Last update 9/7/21

function init() {

	// toggle mobile menu ================

	let toggleStatus = false;
	// Function reveals or hides mobile menu depending on click event. 
	let toggle = function() 
	{
		const menu = document.querySelector('.nav__mobilemenu--wrapper');
		if (menu)
		{
			if (toggleStatus === false)
			{	
				menu.style.display = "grid";
				toggleStatus = true;
				
			} else {
				
				menu.style.display = "none";
				toggleStatus = false;
			}
		}
	}

	let menuHamburger = document.querySelector('.btn__hamburger')
	if (menuHamburger)
	{
		menuHamburger.addEventListener('click', toggle);
	}

	// Changes html button text values depending on browser window width
	function navBtnsChange(navBtns)
	{	
		if (navBtns[0])
		{
			if (window.innerWidth <= 675)
			{	
				navBtns[0].innerHTML = "+Add";
				navBtns[1].innerHTML = "Browse"
			}
			else
			{	
				navBtns[0].innerHTML = "+Add new";
				navBtns[1].innerHTML = "Browse all";
			}
		}
	}
	// Onload function calls navBtnsChange and adds resize listener
	function navBtnsEvents() 
	{	
		const navBtns = document.getElementsByClassName('nav__btn');
		// if exists
		if (navBtns[0]) 
		{	
			// Function called onload
			navBtnsChange(navBtns)
		}
		// Listener added
		window.addEventListener('resize', () => 
		{
			navBtnsChange(navBtns)
		})
	}

	// Pre-selects selected value of an HTML option based on category value from server
	function selectOption()
	{
		// If edit page
		if (window.location.href.match(/(https:\/\/app1\.jasonbergland\.com\/edit\/)\d+/))
		{	
			// Get current category id set by server
			let category = document.querySelector('#current').value;
			console.log(category)
			// Find the correspongind HTML <option> value
			let option = document.getElementsByName(category)[0];
			console.log(option)
			option.setAttribute('selected', 'selected');
		}
	}
	// Manages registration error messages process upon a user submit event
	function verifyReg()
	{
		if (window.location.href === "https://app1.jasonbergland.com/register" ) {
			
			document.querySelector("#reg_form").addEventListener("submit", () =>
			{	
				console.log('verifReg')
				let password, confirmation, user, test2,test3;
				password  = document.querySelector('.password');
				confirmation = document.querySelector('.confirmation');
				user = document.querySelector('.username');
				test2 = document.querySelector('.test2');
				test3 = document.querySelector('.test3');

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
					test2.style.display="block";
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
					test3.style.display="block";
					test3.innerHTML = "Passwords don't match";
					test3.setAttribute("class", "test3 red");
					return false;
				}	
			})
		}
	}
	// Manages registration username error message in real time via ajax request
	function checkUserName(value) 
	{	
		let test = document.querySelector('.test');

		if (value == "")
		{
			test.innerHTML = "";
			test.style.display = "none";
			return false;
		}

		else if (value.length < 3 && !value.length == 0)
		{	
			setTimeout(function() {
				test.style.display = "block";
				test.innerHTML = "Must be at least 3 characters";
				test.setAttribute("class", "test gray");
			}, 100);
		}
		else 
		{
			let param = "username" + "=" + value;
			const xhttp = new XMLHttpRequest();

			// Send paramaters to server function 'check'
			xhttp.open("get", "/check" + "?" + param, true);
			// xhttp.setRequestHeader('Content-Type', 'text/plain');
			
			xhttp.onreadystatechange = function()
			{
				if (xhttp.readyState == 4 && xhttp.status == 200)
				{	
					let data;
					data = JSON.parse(xhttp.responseText);

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
	// Browser fuctions to be called onload
	window.onload = navBtnsEvents();
	window.onload = selectOption();
	window.onload = verifyReg();

	// Upon edit submission, function gathers updated input and makes post request to server for DB updating / 
	// JS then hangles redirecting user to related category page (easier to do with jinja and ajax, then a normal form post)
	function change(itemid)
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
			
			xhttp.open("post", "/change", true);
			xhttp.setRequestHeader('Content-Type', 'application/json');
			xhttp.send(send);
		}
	}



	// Function receives category value, generates new categorgy page with get request
	function cancel(value)
	{	
		return window.location = '/category/' + value;
	}

	// Function deletes entry, reloads page. AJAX is used to have access to window.alert() method during the request handling.
	function deleteEntry(itemId)
	{	
		// Function sends AJAX request and handles the response
		let makeRequest = function()
		{	
			const xhttp = new XMLHttpRequest();

			// When ready
			xhttp.onreadystatechange = function()
			{
				if (xhttp.readyState == 4 && xhttp.status == 200)
				{ 
					let data = xhttp.responseText;
					// If  item is correctly deleted, backend will return True.
					if (data == "True")
					{	
						return document.location.reload();
					}
					
					else if (data == "False")
		    		{	
		    			alert("There was an error deleting the entry")
		    			return window.location = '/login'
		    		}
				}
			}
			xhttp.open("post", "/delete", true);
			xhttp.setRequestHeader('Content-Type', 'application/json');
			xhttp.send(JSON.stringify({itemId: itemId}));
		}
		
		if (window.confirm("You are about to delete this entry. Continue?"))
		{	
			return makeRequest()
		}
		else
		{
			return false
		}
	}	

	//  Retrieves requested edit page
	function editEntry(itemId)
	{	
		window.location = '/edit/' + itemId
	}

	//  function applies click event listeners to dynamically loaded HTML (user's cards)
	function listeners(htmlCol, func)
	{
	 	if (htmlCol)
	 	{
 			for (let i = 0; i < htmlCol.length; i++)
			{
				htmlCol[i].addEventListener('click', () => {
					func(htmlCol[i].parentNode.id)
				})
			}
	 	}
	}

	const editAll = document.getElementsByClassName('edit__all');
	listeners(editAll, editEntry)
	
	const deleteAll = document.getElementsByClassName('delete__all');
	listeners(deleteAll, deleteEntry)
	
	const editCat = document.getElementsByClassName('edit__cat');
	listeners(editCat, editEntry)	

	const deleteCat = document.getElementsByClassName('delete__cat');
	listeners(deleteCat, deleteEntry)
	
	const editSubmit = document.getElementsByClassName('edit__submit');
	listeners(editSubmit, change)
	
	const editCancel = document.getElementsByClassName('edit__cancel');
	listeners(editCancel, cancel)

	// listeners for registration cases ==============
	const regUser = document.querySelector('.register__username');
	if (regUser)
	{
		regUser.addEventListener('keyup', () => {
			checkUserName(regUser.value)
		})
	}
	
	// Login password error message remove
	function pwErrorRemoval(eventElement, messageElement)
	{
		if (eventElement)
		{
			eventElement.addEventListener('keyup', () => {
				messageElement.style.display = "none";
				messageElement.innerHTML = "";
			})
		}
	}

	const password = document.querySelector('.password');
	let test2 = document.querySelector('.test2');
	pwErrorRemoval(password, test2)
	
	const confirmation = document.querySelector('.confirmation');
	let test3 = document.querySelector('.test3');
	pwErrorRemoval(confirmation, test3)

}
window.addEventListener('load', init)
