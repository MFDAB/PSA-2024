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

// Filtering function for each column
function filterTable() {
    const cargoIDFilter = document.getElementById('cargo-id-filter').value.toLowerCase();
    const statusFilter = document.getElementById('status-filter').value.toLowerCase();
    const tagsFilter = document.getElementById('tags-filter').value.toLowerCase();
    const originFilter = document.getElementById('origin-filter').value.toLowerCase();
    const destinationFilter = document.getElementById('destination-filter').value.toLowerCase();
    const assignedContainerFilter = document.getElementById('assigned-container-filter').value.toLowerCase();  // New filter for assigned container

    const table = document.getElementById('cargo-table');
    const rows = table.getElementsByTagName('tr');

    // Loop through table rows
    for (let i = 1; i < rows.length; i++) {
        let cargoID = rows[i].getElementsByTagName('td')[0].textContent.toLowerCase();
        let status = rows[i].getElementsByTagName('td')[3].textContent.toLowerCase();
        let tags = rows[i].getElementsByTagName('td')[6].textContent.toLowerCase();
        let origin = rows[i].getElementsByTagName('td')[8].textContent.toLowerCase();
        let destination = rows[i].getElementsByTagName('td')[9].textContent.toLowerCase();
        let assignedContainer = rows[i].getElementsByTagName('td')[14].textContent.toLowerCase();  // Added assigned container

        let showRow = true;

        // Apply filters
        if (cargoIDFilter && !cargoID.includes(cargoIDFilter)) showRow = false;
        if (statusFilter && !status.includes(statusFilter)) showRow = false;
        if (tagsFilter && !tags.includes(tagsFilter)) showRow = false;
        if (originFilter && !origin.includes(originFilter)) showRow = false;
        if (destinationFilter && !destination.includes(destinationFilter)) showRow = false;
        if (assignedContainerFilter && !assignedContainer.includes(assignedContainerFilter)) showRow = false;  // Added container filter

        // Show or hide rows based on filters
        if (showRow) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

// Event listeners for filters
document.getElementById('cargo-id-filter').addEventListener('input', filterTable);
document.getElementById('status-filter').addEventListener('input', filterTable);
document.getElementById('tags-filter').addEventListener('input', filterTable);
document.getElementById('origin-filter').addEventListener('input', filterTable);
document.getElementById('destination-filter').addEventListener('input', filterTable);
document.getElementById('assigned-container-filter').addEventListener('input', filterTable);  // Event listener for assigned container