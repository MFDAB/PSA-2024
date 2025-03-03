// SIDEBAR DROPDOWN
const allDropdown = document.querySelectorAll('#sidebar .side-dropdown');
const sidebar = document.getElementById('sidebar');

allDropdown.forEach(item=> {
	const a = item.parentElement.querySelector('a:first-child');
	a.addEventListener('click', function (e) {
		e.preventDefault();

		if(!this.classList.contains('active')) {
			allDropdown.forEach(i=> {
				const aLink = i.parentElement.querySelector('a:first-child');

				aLink.classList.remove('active');
				i.classList.remove('show');
			})
		}

		this.classList.toggle('active');
		item.classList.toggle('show');
	})
})





// SIDEBAR COLLAPSE
const toggleSidebar = document.querySelector('nav .toggle-sidebar');
const allSideDivider = document.querySelectorAll('#sidebar .divider');

if(sidebar.classList.contains('hide')) {
	allSideDivider.forEach(item=> {
		item.textContent = '-'
	})
	allDropdown.forEach(item=> {
		const a = item.parentElement.querySelector('a:first-child');
		a.classList.remove('active');
		item.classList.remove('show');
	})
} else {
	allSideDivider.forEach(item=> {
		item.textContent = item.dataset.text;
	})
}

toggleSidebar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');

	if(sidebar.classList.contains('hide')) {
		allSideDivider.forEach(item=> {
			item.textContent = '-'
		})

		allDropdown.forEach(item=> {
			const a = item.parentElement.querySelector('a:first-child');
			a.classList.remove('active');
			item.classList.remove('show');
		})
	} else {
		allSideDivider.forEach(item=> {
			item.textContent = item.dataset.text;
		})
	}
})




sidebar.addEventListener('mouseleave', function () {
	if(this.classList.contains('hide')) {
		allDropdown.forEach(item=> {
			const a = item.parentElement.querySelector('a:first-child');
			a.classList.remove('active');
			item.classList.remove('show');
		})
		allSideDivider.forEach(item=> {
			item.textContent = '-'
		})
	}
})



sidebar.addEventListener('mouseenter', function () {
	if(this.classList.contains('hide')) {
		allDropdown.forEach(item=> {
			const a = item.parentElement.querySelector('a:first-child');
			a.classList.remove('active');
			item.classList.remove('show');
		})
		allSideDivider.forEach(item=> {
			item.textContent = item.dataset.text;
		})
	}
})




// PROFILE DROPDOWN
const profile = document.querySelector('nav .profile');
const imgProfile = profile.querySelector('img');
const dropdownProfile = profile.querySelector('.profile-link');

imgProfile.addEventListener('click', function () {
	dropdownProfile.classList.toggle('show');
})




// MENU
const allMenu = document.querySelectorAll('main .content-data .head .menu');

allMenu.forEach(item=> {
	const icon = item.querySelector('.icon');
	const menuLink = item.querySelector('.menu-link');

	icon.addEventListener('click', function () {
		menuLink.classList.toggle('show');
	})
})



window.addEventListener('click', function (e) {
	if(e.target !== imgProfile) {
		if(e.target !== dropdownProfile) {
			if(dropdownProfile.classList.contains('show')) {
				dropdownProfile.classList.remove('show');
			}
		}
	}

	allMenu.forEach(item=> {
		const icon = item.querySelector('.icon');
		const menuLink = item.querySelector('.menu-link');

		if(e.target !== icon) {
			if(e.target !== menuLink) {
				if (menuLink.classList.contains('show')) {
					menuLink.classList.remove('show')
				}
			}
		}
	})
})





// PROGRESSBAR
const allProgress = document.querySelectorAll('main .card .progress');

allProgress.forEach(item=> {
	item.style.setProperty('--value', item.dataset.value)
})






// APEXCHART
var options = {
  series: [{
  name: 'series1',
  data: [31, 40, 28, 51, 42, 109, 100]
}, {
  name: 'series2',
  data: [11, 32, 45, 32, 34, 52, 41]
}],
  chart: {
  height: 350,
  type: 'area'
},
dataLabels: {
  enabled: false
},
stroke: {
  curve: 'smooth'
},
xaxis: {
  type: 'datetime',
  categories: ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z", "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z", "2018-09-19T06:30:00.000Z"]
},
tooltip: {
  x: {
    format: 'dd/MM/yy HH:mm'
  },
},
};

var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();

document.addEventListener('DOMContentLoaded', function () {
	fetch('/get-ports') // Adjust the endpoint according to your backend
		.then(response => response.json())
		.then(data => {
			const originOptions = document.getElementById('origin-options');
			const destinationOptions = document.getElementById('destination-options');

			data.ports.forEach(port => {
				const option = document.createElement('option');
				option.value = `${port.city}, ${port.country} (${port.port})`;
				originOptions.appendChild(option);
				destinationOptions.appendChild(option.cloneNode(true));
			});
		})
		.catch(error => console.error('Error fetching port data:', error));
});

// Handle form submission
document.getElementById('shipment-form').addEventListener('submit', function (e) {
	e.preventDefault();

	const formData = new FormData(this);
	const formJSON = Object.fromEntries(formData.entries());

	console.log(formJSON);  // You can send this data to your server

	// Fetch request to send the form data to the server
	fetch('/submit-shipment', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(formJSON),
	})
	.then(response => response.json())
	.then(result => {
		alert(result.message);
	})
	.catch(error => console.error('Error submitting form:', error));
});


document.getElementById('shipment-form').addEventListener('submit', function(event) {
	event.preventDefault();  // Prevent form from submitting the default way
	
	// Collect form data
	const formData = new FormData(this);
	const data = {
		name: formData.get('name'),
		business_name: formData.get('business-name'),
		chat_id: formData.get('chat-id'),  // Will be empty or populated if needed
		phone_number: formData.get('phone-number'),
		business_email: formData.get('business-email'),
		dimensions: {
			length: formData.get('length'),
			width: formData.get('width'),
			height: formData.get('height')
		},
		weight: formData.get('weight'),
		origin: formData.get('origin'),
		destination: formData.get('destination'),
		send_off_date: formData.get('send-off-date'),
		arrival_date: formData.get('arrival-date'),
		flexidate_tolerance: formData.get('flexidate'),
		tags: formData.getAll('tags[]'),  // Since 'tags' is a multi-select, use getAll
		additional_comments: formData.get('comments')
	};

	console.log('Data to send:', data); // Debugging: See the data before sending
	
	// Send the data via a POST request
	fetch('/submit-cargo', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(data),
	})
	.then(response => response.json())
	.then(result => {
		// Process the result
		alert(result.message);  // Alert success message
		console.log('Success:', result);
	})
	.catch(error => {
		console.error('Error:', error);
	});
});