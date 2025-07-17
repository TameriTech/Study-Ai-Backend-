// Function to load navigation (header)
function loadNavigation() {
  const currentPage = window.location.pathname.split("/").pop().toLowerCase();

  const pages = [
    { name: "Accueil", path: "index.html" },
    { name: "À Propos", path: "about.html" },
    { name: "Services", path: "services.html" },
    { name: "Projets", path: "projects.html" },
    { name: "Contact", path: "contact.html" }
  ];

  const nav = `
    <nav class="bg-stone-950 text-neutral-100 font-poppins shadow-lg">
      <div class="max-w-[1384px] mx-auto px-6 sm:px-8 lg:px-10">
        <div class="flex items-center justify-between h-20">
          <div class="flex-shrink-0">
            <a href="index.html" aria-label="Godlove Empire Accueil">
              <img class="h-10 w-auto" src="https://cdn.builder.io/api/v1/image/assets/TEMP/ad855b78a94778349eb54c38c40e26157a7a8e38?width=158" alt="Logo Godlove">
            </a>
          </div>

          <!-- Desktop Menu -->
          <div class="hidden md:flex space-x-6">
            ${pages.map(({ name, path }) => {
              const isActive = currentPage === path.toLowerCase();
              return `
              <a href="${path}" 
                 class="px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200
                 ${isActive ? 'text-red-500 border-b-2 border-red-600 font-semibold' : 'text-neutral-300 hover:text-red-400 hover:bg-red-900/20'}"
                 aria-current="${isActive ? 'page' : undefined}">
                ${name}
              </a>
              `;
            }).join("")}
          </div>

          <!-- Language Switcher (Desktop) - KEEP UNCHANGED -->
          <div class="flex flex-col gap-2.5 items-start rounded-xl">
            <div class="flex gap-2 justify-center items-center px-4 py-3.5 rounded-lg">
              <!-- Language SVGs here, unchanged -->
              <div>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="globe-icon" style="display: flex; width: 20px; height: 20px; justify-content: center; align-items: center; flex-shrink: 0;">
                  <path opacity="0.4" d="M6.37505 17.425C6.35005 17.425 6.31672 17.4416 6.29172 17.4416C4.67505 16.6416 3.35838 15.3166 2.55005 13.7C2.55005 13.675 2.56672 13.6416 2.56672 13.6166C3.58338 13.9166 4.63338 14.1416 5.67505 14.3166C5.85838 15.3666 6.07505 16.4083 6.37505 17.425Z" fill="#D50706"/>
                  <path opacity="0.4" d="M17.45 13.7083C16.625 15.3666 15.25 16.7083 13.575 17.5166C13.8916 16.4583 14.1583 15.3916 14.3333 14.3166C15.3833 14.1416 16.4166 13.9166 17.4333 13.6166C17.425 13.65 17.45 13.6833 17.45 13.7083Z" fill="#D50706"/>
                  <path opacity="0.4" d="M17.5166 6.42494C16.4666 6.10828 15.4083 5.84994 14.3333 5.66661C14.1583 4.59161 13.9 3.52494 13.575 2.48328C15.3 3.30828 16.6916 4.69994 17.5166 6.42494Z" fill="#D50706"/>
                  <path opacity="0.4" d="M6.37494 2.57505C6.07494 3.59172 5.85828 4.62505 5.68328 5.67505C4.60828 5.84172 3.54161 6.10838 2.48328 6.42505C3.29161 4.75005 4.63328 3.37505 6.29161 2.55005C6.31661 2.55005 6.34994 2.57505 6.37494 2.57505Z" fill="#D50706"/>
                  <path d="M12.9083 5.49163C10.975 5.27496 9.02501 5.27496 7.09167 5.49163C7.30001 4.34996 7.56667 3.20829 7.94167 2.10829C7.95834 2.04163 7.95001 1.99163 7.95834 1.92496C8.61667 1.76663 9.29167 1.66663 10 1.66663C10.7 1.66663 11.3833 1.76663 12.0333 1.92496C12.0417 1.99163 12.0417 2.04163 12.0583 2.10829C12.4333 3.21663 12.7 4.34996 12.9083 5.49163Z" fill="#D50706"/>
                  <path d="M5.49163 12.9083C4.34163 12.7 3.20829 12.4333 2.10829 12.0583C2.04163 12.0417 1.99163 12.05 1.92496 12.0417C1.76663 11.3833 1.66663 10.7083 1.66663 10C1.66663 9.30001 1.76663 8.61667 1.92496 7.96667C1.99163 7.95834 2.04163 7.95834 2.10829 7.94167C3.21663 7.57501 4.34163 7.30001 5.49163 7.09167C5.28329 9.02501 5.28329 10.975 5.49163 12.9083Z" fill="#D50706"/>
                  <path d="M18.3333 10C18.3333 10.7083 18.2333 11.3833 18.075 12.0417C18.0083 12.05 17.9583 12.0417 17.8916 12.0583C16.7833 12.425 15.65 12.7 14.5083 12.9083C14.725 10.975 14.725 9.02501 14.5083 7.09167C15.65 7.30001 16.7916 7.56667 17.8916 7.94167C17.9583 7.95834 18.0083 7.96667 18.075 7.96667C18.2333 8.62501 18.3333 9.30001 18.3333 10Z" fill="#D50706"/>
                  <path d="M12.9083 14.5084C12.7 15.6584 12.4333 16.7917 12.0583 17.8917C12.0417 17.9584 12.0417 18.0084 12.0333 18.075C11.3833 18.2334 10.7 18.3334 10 18.3334C9.29167 18.3334 8.61667 18.2334 7.95834 18.075C7.95001 18.0084 7.95834 17.9584 7.94167 17.8917C7.57501 16.7834 7.30001 15.6584 7.09167 14.5084C8.05834 14.6167 9.02501 14.6917 10 14.6917C10.975 14.6917 11.95 14.6167 12.9083 14.5084Z" fill="#D50706"/>
                  <path d="M13.1361 13.1361C11.0518 13.399 8.9481 13.399 6.86385 13.1361C6.60088 11.0518 6.60088 8.9481 6.86385 6.86385C8.9481 6.60088 11.0518 6.60088 13.1361 6.86385C13.399 8.9481 13.399 11.0518 13.1361 13.1361Z" fill="#D50706"/>
                </svg>
              </div>
              <span class="text-base leading-5 text-red-700 font-semibold">Fr</span>
              <div>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="arrow-down-icon" style="display: flex; width: 20px; height: 20px; justify-content: center; align-items: center; flex-shrink: 0;">
                  <path opacity="0.4" d="M12.9 11.025L9.7417 6.81665H5.0667C4.2667 6.81665 3.8667 7.78332 4.43337 8.34998L8.75003 12.6666C9.4417 13.3583 10.5667 13.3583 11.2584 12.6666L12.9 11.025Z" fill="#D50706"/>
                  <path d="M14.9334 6.81665H9.7417L12.9 11.025L15.575 8.34998C16.1334 7.78332 15.7334 6.81665 14.9334 6.81665Z" fill="#D50706"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button id="mobile-menu-toggle" aria-label="Menu mobile" class="text-neutral-300 hover:text-red-400 focus:outline-none focus:ring-2 focus:ring-red-500 rounded">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div id="mobile-menu" class="md:hidden hidden px-6 pb-6 space-y-1 bg-stone-950">
        ${pages.map(({ name, path }) => {
          const isActive = currentPage === path.toLowerCase();
          return `
          <a href="${path}" class="block px-4 py-2 rounded-md w-fit text-base font-medium transition-colors duration-200
            ${isActive ? 'text-red-500 border-b-2 border-red-600 font-semibold' : 'text-neutral-300 hover:text-red-400 hover:bg-red-900/20'}"
            aria-current="${isActive ? 'page' : undefined}">
            ${name}
          </a>
          `;
        }).join("")}
      </div>
    </nav>
  `;

  // Inject nav into header
  document.querySelector("header").innerHTML = nav;

  // Attach mobile menu toggle click listener
  const toggleBtn = document.getElementById("mobile-menu-toggle");
  const mobileMenu = document.getElementById("mobile-menu");

  if (toggleBtn && mobileMenu) {
    toggleBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
    });
  }
}

// Function to load footer
function loadFooter() {
  const footer = `
  <footer class="bg-stone-900 text-neutral-200 font-poppins py-12 px-6">
  <div class="max-w-6xl mx-auto">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-12 lg:gap-16">
      <!-- Godlove Empire Section -->
      <div class="md:col-span-1 flex flex-col items-center md:items-start">
        <h3 class="text-3xl font-cormorant font-semibold mb-5 text-red-600 text-center md:text-left">Godlove Empire</h3>
        <p class="mb-6 leading-relaxed max-w-xs text-center md:text-left">
          Création d'identités visuelles inspirantes depuis 2017.
        </p>
        <div class="flex gap-4 justify-center md:justify-start">
          <a href="#" aria-label="Facebook" class="w-10 h-10 rounded-full bg-stone-700 flex items-center justify-center hover:bg-red-700 transition-colors">
            <i class="fab fa-facebook-f"></i>
          </a>
          <a href="#" aria-label="Twitter" class="w-10 h-10 rounded-full bg-stone-700 flex items-center justify-center hover:bg-red-700 transition-colors">
            <i class="fab fa-twitter"></i>
          </a>
          <a href="#" aria-label="Instagram" class="w-10 h-10 rounded-full bg-stone-700 flex items-center justify-center hover:bg-red-700 transition-colors">
            <i class="fab fa-instagram"></i>
          </a>
        </div>
      </div>

      <!-- Entreprise Section -->
      <div class="flex flex-col items-center md:items-start">
        <h4 class="text-xl font-semibold mb-5 text-center md:text-left">Entreprise</h4>
        <ul class="space-y-3 font-medium text-center md:text-left">
          <li><a href="about.html" class="hover:text-red-500 transition-colors">À Propos</a></li>
          <li><a href="services.html" class="hover:text-red-500 transition-colors">Services</a></li>
          <li><a href="portfolio.html" class="hover:text-red-500 transition-colors">Portfolio</a></li>
          <li><a href="contact.html" class="hover:text-red-500 transition-colors">Contact</a></li>
          <li><a href="faq.html" class="hover:text-red-500 transition-colors">FAQ</a></li>
        </ul>
      </div>

      <!-- Services Section -->
      <div class="flex flex-col items-center md:items-start">
        <h4 class="text-xl font-semibold mb-5 text-center md:text-left">Services</h4>
        <ul class="space-y-3 font-medium text-center md:text-left">
          <li><a href="#" class="hover:text-red-500 transition-colors">Branding</a></li>
          <li><a href="#" class="hover:text-red-500 transition-colors">Photographie</a></li>
          <li><a href="#" class="hover:text-red-500 transition-colors">Impression</a></li>
          <li><a href="#" class="hover:text-red-500 transition-colors">Design Graphique</a></li>
        </ul>
      </div>

      <!-- Contact Section -->
      <div class="flex flex-col items-center md:items-start">
        <h4 class="text-xl font-semibold mb-5 text-center md:text-left">Contact</h4>
        <div class="text-center md:text-left">
          <p class="mb-2 font-medium">Douala, Cameroun</p>
          <p class="mb-2 font-medium">+237 650 000 000</p>
          <p class="font-medium">info@godloveempire.com</p>
        </div>
      </div>
    </div>

    <div class="mt-14 text-center text-neutral-400 text-sm select-none">
      &copy; ${new Date().getFullYear()} Godlove Empire. Tous droits réservés.
    </div>
  </div>
</footer>
  `;
  document.querySelector('footer').innerHTML = footer;
}
document.addEventListener('DOMContentLoaded', function () {
  loadNavigation();
  loadFooter();
});