"""Geographic reference data for tutor location fields.

Contains:
- NIGERIAN_STATES: the 36 states plus the FCT (Abuja) = 37 entries.
- NIGERIAN_LGAS: a mapping of each state to its Local Government Areas.
- COUNTRIES_BY_CONTINENT: countries grouped by continent (Nigeria is the default).
"""

NIGERIAN_STATES = [
    "Abia",
    "Adamawa",
    "Akwa Ibom",
    "Anambra",
    "Bauchi",
    "Bayelsa",
    "Benue",
    "Borno",
    "Cross River",
    "Delta",
    "Ebonyi",
    "Edo",
    "Ekiti",
    "Enugu",
    "Gombe",
    "Imo",
    "Jigawa",
    "Kaduna",
    "Kano",
    "Katsina",
    "Kebbi",
    "Kogi",
    "Kwara",
    "Lagos",
    "Nasarawa",
    "Niger",
    "Ogun",
    "Ondo",
    "Osun",
    "Oyo",
    "Plateau",
    "Rivers",
    "Sokoto",
    "Taraba",
    "Yobe",
    "Zamfara",
    "FCT (Abuja)",
]

NIGERIAN_LGAS = {
    "Abia": [
        "Aba North", "Aba South", "Arochukwu", "Bende", "Ikwuano",
        "Isiala Ngwa North", "Isiala Ngwa South", "Isuikwuato", "Obi Ngwa",
        "Ohafia", "Osisioma", "Ugwunagbo", "Ukwa East", "Ukwa West",
        "Umuahia North", "Umuahia South", "Umu Nneochi",
    ],
    "Adamawa": [
        "Demsa", "Fufore", "Ganye", "Girei", "Gombi", "Guyuk", "Hong",
        "Jada", "Lamurde", "Madagali", "Maiha", "Mayo Belwa", "Michika",
        "Mubi North", "Mubi South", "Numan", "Shelleng", "Song", "Toungo",
        "Yola North", "Yola South",
    ],
    "Akwa Ibom": [
        "Abak", "Eastern Obolo", "Eket", "Esit Eket", "Essien Udim",
        "Etim Ekpo", "Etinan", "Ibesikpo Asutan", "Ibiono-Ibom", "Ika",
        "Ikono", "Ikot Ekpene", "Ini", "Itu", "Mbo", "Mkpat-Enin",
        "Nsit-Ibom", "Nsit-Ubium", "Obot Akara", "Okobo", "Onna", "Oron",
        "Oruk Anam", "Udung-Uko", "Ukanafun", "Uruan", "Urue-Offong/Oruko",
        "Uyo",
    ],
    "Anambra": [
        "Aguata", "Anambra East", "Anambra West", "Anaocha", "Awka North",
        "Awka South", "Ayamelum", "Dunukofia", "Ekwusigo", "Idemili North",
        "Idemili South", "Ihiala", "Njikoka", "Nnewi North", "Nnewi South",
        "Ogbaru", "Onitsha North", "Onitsha South", "Orumba North",
        "Orumba South", "Oyi",
    ],
    "Bauchi": [
        "Alkaleri", "Bauchi", "Bogoro", "Dambam", "Damban", "Darazo",
        "Dass", "Gamawa", "Giade", "Itas/Gadau", "Jama'are", "Katagum",
        "Kirfi", "Misau", "Ningi", "Shira", "Tafawa Balewa", "Toro",
        "Warji", "Zaki",
    ],
    "Bayelsa": [
        "Brass", "Ekeremor", "Kolokuma/Opokuma", "Nembe", "Ogbia",
        "Sagbama", "Southern Ijaw", "Yenagoa",
    ],
    "Benue": [
        "Ado", "Agatu", "Apa", "Buruku", "Gboko", "Guma", "Gwer East",
        "Gwer West", "Katsina-Ala", "Konshisha", "Kwande", "Logo",
        "Makurdi", "Obi", "Ogbadibo", "Oju", "Okpokwu", "Ohimini",
        "Orokam", "Tarka", "Ukum", "Ushongo", "Vandeikya",
    ],
    "Borno": [
        "Abadam", "Askira/Uba", "Bama", "Bayo", "Biu", "Chibok", "Damboa",
        "Dikwa", "Gubio", "Guzamala", "Gwoza", "Hawul", "Jere", "Kaga",
        "Kala/Balge", "Konduga", "Kukawa", "Kwaya Kusar", "Mafa",
        "Maiduguri", "Magumeri", "Marte", "Mobbar", "Monguno", "Ngala",
        "Nganzai", "Shani",
    ],
    "Cross River": [
        "Abi", "Akamkpa", "Akpabuyo", "Bakassi", "Bekwarra", "Biase",
        "Boki", "Calabar Municipal", "Calabar South", "Etung", "Ikom",
        "Obanliku", "Obubra", "Odukpani", "Ogoja", "Yakurr", "Yala",
    ],
    "Delta": [
        "Aniocha North", "Aniocha South", "Bomadi", "Burutu",
        "Ethiope East", "Ethiope West", "Ika North East", "Ika South",
        "Isoko North", "Isoko South", "Ndokwa East", "Ndokwa West",
        "Okpe", "Oshimili North", "Oshimili South", "Patani", "Sapele",
        "Udu", "Ughelli North", "Ughelli South", "Ukwuani", "Uvwie",
        "Warri North", "Warri South", "Warri South West",
    ],
    "Ebonyi": [
        "Abakaliki", "Afikpo North", "Afikpo South", "Ebonyi", "Ezza North",
        "Ezza South", "Ikwo", "Ishielu", "Ivo", "Ohaozara", "Ohaukwu",
        "Onicha", "Izzi",
    ],
    "Edo": [
        "Akoko-Edo", "Egor", "Esan Central", "Esan North-East",
        "Esan South-East", "Esan West", "Etsako Central", "Etsako East",
        "Etsako West", "Igueben", "Ikpoba-Okha", "Oredo", "Orhionmwon",
        "Ovia North-East", "Ovia South-West", "Owan East", "Owan West",
        "Uhunmwonde",
    ],
    "Ekiti": [
        "Ado", "Efon", "Ekiti East", "Ekiti South-West", "Ekiti West",
        "Emure", "Gbonyin", "Ido/Osi", "Ijero", "Ikere", "Ikole",
        "Ilejemeje", "Irepodun/Ifelodun", "Ise/Orun", "Moba", "Oye",
    ],
    "Enugu": [
        "Aninri", "Awgu", "Enugu East", "Enugu North", "Enugu South",
        "Ezeagu", "Igbo Etiti", "Igbo Eze North", "Igbo Eze South",
        "Isi Uzo", "Nkanu East", "Nkanu West", "Nsukka", "Oji River",
        "Udi", "Uzo Uwani",
    ],
    "Gombe": [
        "Akko", "Balanga", "Billiri", "Dukku", "Funakaye", "Gombe",
        "Kaltungo", "Kwami", "Nafada", "Shongom", "Yamaltu/Deba",
    ],
    "Imo": [
        "Aboh Mbaise", "Ahiazu Mbaise", "Ehime Mbano", "Ezinihitte",
        "Ideato North", "Ideato South", "Ihitte/Uboma", "Ikeduru",
        "Isiala Mbano", "Isu", "Mbaitoli", "Ngor Okpala", "Njaba",
        "Nkwerre", "Nwangele", "Obowo", "Oguta", "Ohaji/Egbema",
        "Okigwe", "Onuimo", "Orlu", "Orsu", "Oru East", "Oru West",
        "Owerri Municipal", "Owerri North", "Owerri West",
    ],
    "Jigawa": [
        "Auyo", "Babura", "Biriniwa", "Birnin Kudu", "Buji", "Dutse",
        "Gagarawa", "Garki", "Gumel", "Guri", "Gwaram", "Gwiwa",
        "Hadejia", "Jahun", "Kafin Hausa", "Kazaure", "Kiri Kasama",
        "Kiyawa", "Maigatari", "Malam Madori", "Miga", "Ringim", "Roni",
        "Sule Tankarkar", "Taura", "Yankwashi",
    ],
    "Kaduna": [
        "Birnin Gwari", "Chikun", "Giwa", "Igabi", "Ikara", "Jaba",
        "Jema'a", "Kachia", "Kaduna North", "Kaduna South", "Kagarko",
        "Kajuru", "Kaura", "Kauru", "Kubau", "Kudan", "Lere", "Makarfi",
        "Sabon Gari", "Sanga", "Soba", "Zangon Kataf", "Zaria",
    ],
    "Kano": [
        "Ajingi", "Albasu", "Bagwai", "Bebeji", "Bichi", "Bunkure", "Dala",
        "Dambatta", "Dawakin Kudu", "Dawakin Tofa", "Doguwa", "Fagge",
        "Gabasawa", "Garko", "Garun Mallam", "Gaya", "Gezawa", "Gwale",
        "Gwarzo", "Kabo", "Kano Municipal", "Karaye", "Kibiya", "Kiru",
        "Kumbotso", "Kunchi", "Kura", "Madobi", "Makoda", "Minjibir",
        "Nasarawa", "Rano", "Rimin Gado", "Rogo", "Shanono", "Sumaila",
        "Takai", "Tarauni", "Tofa", "Tsanyawa", "Tudun Wada", "Ungogo",
        "Warawa", "Wudil",
    ],
    "Katsina": [
        "Bakori", "Batagarawa", "Batsari", "Baure", "Bindawa", "Charanchi",
        "Dandume", "Danja", "Dan Musa", "Daura", "Dutsi", "Dutsin Ma",
        "Faskari", "Funtua", "Ingawa", "Jibia", "Kafur", "Kaita",
        "Kankara", "Kankia", "Katsina", "Kurfi", "Kusada", "Mai'Adua",
        "Malumfashi", "Mani", "Mashi", "Musawa", "Matazu", "Rimi",
        "Sabuwa", "Safana", "Sandamu", "Zango",
    ],
    "Kebbi": [
        "Aleiro", "Arewa Dandi", "Argungu", "Augie", "Bagudo",
        "Birnin Kebbi", "Bunza", "Dandi", "Fakai", "Gwandu", "Jega",
        "Kalgo", "Koko/Besse", "Maiyama", "Ngaski", "Sakaba", "Shanga",
        "Suru", "Wasagu/Danko", "Yauri", "Zuru",
    ],
    "Kogi": [
        "Adavi", "Ajaokuta", "Ankpa", "Bassa", "Dekina", "Ibaji",
        "Igalamela-Odolu", "Ijumu", "Kabba/Bunu", "Kogi", "Lokoja",
        "Mopa-Muro", "Ofu", "Ogori/Magongo", "Okehi", "Okene",
        "Olamaboro", "Omala", "Yagba East", "Yagba West", "Lokoja",
    ],
    "Kwara": [
        "Asa", "Baruten", "Edu", "Ekiti", "Ifelodun", "Ilorin East",
        "Ilorin North", "Ilorin South", "Irepodun", "Isin", "Kaiama",
        "Moro", "Offa", "Oke Ero", "Oyun", "Pategi",
    ],
    "Lagos": [
        "Agege", "Ajeromi-Ifelodun", "Alimosho", "Amuwo-Odofin", "Apapa",
        "Badagry", "Epe", "Eti-Osa", "Ibeju-Lekki", "Ifako-Ijaiye",
        "Ikeja", "Ikorodu", "Kosofe", "Lagos Island", "Lagos Mainland",
        "Mushin", "Ojo", "Oshodi-Isolo", "Shomolu", "Surulere",
    ],
    "Nasarawa": [
        "Akwanga", "Awe", "Doma", "Karu", "Keana", "Keffi", "Kokona",
        "Lafia", "Nasarawa", "Nasarawa Egon", "Obi", "Toto", "Wamba",
    ],
    "Niger": [
        "Agaie", "Agwara", "Bida", "Borgu", "Bosso", "Chanchaga",
        "Edati", "Gbako", "Gurara", "Katcha", "Kontagora", "Lapai",
        "Lavun", "Magama", "Mariga", "Mashegu", "Mokwa", "Muya",
        "Paikoro", "Rafi", "Rijau", "Shiroro", "Suleja", "Tafa",
        "Wushishi",
    ],
    "Ogun": [
        "Abeokuta North", "Abeokuta South", "Ado-Odo/Ota", "Egbado North",
        "Egbado South", "Ewekoro", "Ifo", "Ijebu East", "Ijebu North",
        "Ijebu North East", "Ijebu Ode", "Ikenne", "Imeko Afon", "Ipokia",
        "Obafemi Owode", "Odeda", "Odogbolu", "Ogun Waterside",
        "Remo North", "Shagamu",
    ],
    "Ondo": [
        "Akoko North-East", "Akoko North-West", "Akoko South-East",
        "Akoko South-West", "Akure North", "Akure South", "Ese Odo",
        "Idanre", "Ifedore", "Ilaje", "Ile Oluji/Okeigbo", "Irele",
        "Odigbo", "Okitipupa", "Ondo East", "Ondo West", "Ose", "Owo",
    ],
    "Osun": [
        "Atakunmosa East", "Atakunmosa West", "Aiyedaade", "Aiyedire",
        "Boluwaduro", "Boripe", "Ede North", "Ede South", "Egbedore",
        "Ejigbo", "Ife Central", "Ife East", "Ife North", "Ife South",
        "Ifedayo", "Ifelodun", "Ila", "Ilesa East", "Ilesa West",
        "Irepodun", "Irewole", "Isokan", "Iwo", "Obokun", "Ola Oluwa",
        "Olorunda", "Oriade", "Orolu", "Osogbo",
    ],
    "Oyo": [
        "Afijio", "Akinyele", "Atiba", "Atisbo", "Egbeda",
        "Ibadan North", "Ibadan North-East", "Ibadan North-West",
        "Ibadan South-East", "Ibadan South-West", "Ibarapa Central",
        "Ibarapa East", "Ibarapa North", "Ido", "Irepo", "Iseyin",
        "Itesiwaju", "Iwajowa", "Kajola", "Lagelu", "Ogbomoso North",
        "Ogbomoso South", "Ogo Oluwa", "Olorunsogo", "Ona Ara", "Orelope",
        "Ori Ire", "Oyo East", "Oyo West", "Saki East", "Saki West",
        "Surulere",
    ],
    "Plateau": [
        "Barkin Ladi", "Bassa", "Bokkos", "Jos East", "Jos North",
        "Jos South", "Kanam", "Kanke", "Langtang North", "Langtang South",
        "Mangu", "Mikang", "Pankshin", "Qua'an Pan", "Riyom", "Shendam",
        "Wase",
    ],
    "Rivers": [
        "Abua/Odual", "Ahoada East", "Ahoada West", "Akuku-Toru",
        "Andoni", "Asari-Toru", "Bonny", "Degema", "Eleme", "Emohua",
        "Etche", "Gokana", "Ikwerre", "Khana", "Obio-Akpor",
        "Ogba/Egbema/Ndoni", "Ogu/Bolo", "Okrika", "Omuma",
        "Opobo/Nkoro", "Oyigbo", "Port Harcourt", "Tai",
    ],
    "Sokoto": [
        "Binji", "Bodinga", "Dange Shuni", "Gada", "Goronyo", "Gudu",
        "Gwadabawa", "Illela", "Isa", "Kebbe", "Kware", "Rabah",
        "Sabon Birni", "Shagari", "Silame", "Sokoto North", "Sokoto South",
        "Tambuwal", "Tangaza", "Tureta", "Wamako", "Wurno", "Yabo",
    ],
    "Taraba": [
        "Ardo Kola", "Bali", "Donga", "Gashaka", "Gassol", "Ibi",
        "Jalingo", "Karim Lamido", "Kurmi", "Lau", "Sardauna", "Takum",
        "Ussa", "Wukari", "Yorro", "Zing",
    ],
    "Yobe": [
        "Bade", "Bursari", "Damaturu", "Fika", "Fune", "Geidam", "Gujba",
        "Gulani", "Jakusko", "Karasuwa", "Machina", "Nangere", "Nguru",
        "Potiskum", "Tarmuwa", "Yunusari", "Yusufari",
    ],
    "Zamfara": [
        "Anka", "Bakura", "Birnin Magaji/Kiyaw", "Bukkuyum", "Bungudu",
        "Gummi", "Gusau", "Kaura Namoda", "Maradun", "Maru", "Shinkafi",
        "Talata Mafara", "Tsafe", "Zurmi",
    ],
    "FCT (Abuja)": [
        "Abaji", "Abuja Municipal (AMAC)", "Bwari", "Gwagwalada", "Kuje",
        "Kwali",
    ],
}

WORLD_SUBDIVISIONS = {
    "Nigeria": {
        "state_label": "State",
        "lga_label": "Local Government",
        "states": NIGERIAN_STATES,
        "lgas": NIGERIAN_LGAS,
    },
    "Madagascar": {
        "state_label": "Region / Province",
        "lga_label": "District / City",
        "states": [
            "Analamanga", "Antsinanana", "Vakinankaratra", "Boeny", "Diana",
            "Atsimo-Andrefana", "Haute Matsiatra", "Sava", "Menabe", "Sofia",
            "Alaotra-Mangoro", "Anosy", "Androy", "Itasy", "Ihorombe"
        ],
        "lgas": {
            "Analamanga": ["Antananarivo Renivohitra", "Ambohidratrimo", "Andramasina", "Anjozorobe", "Ankazobe", "Manjakandriana"],
            "Antsinanana": ["Toamasina I", "Toamasina II", "Brickaville", "Mahanoro", "Marolambo", "Vatomandry"],
            "Vakinankaratra": ["Antsirabe I", "Antsirabe II", "Ambatolampy", "Betafo", "Faratsiho"],
            "Boeny": ["Mahajanga I", "Mahajanga II", "Ambato-Boeni", "Marovoay", "Mitsinjo"],
            "Diana": ["Antsiranana I", "Antsiranana II", "Ambanja", "Ambilobe", "Nosy Be"],
        }
    },
    "Ghana": {
        "state_label": "Region",
        "lga_label": "District / City",
        "states": [
            "Greater Accra", "Ashanti", "Western", "Eastern", "Central",
            "Northern", "Volta", "Upper East", "Upper West", "Bono",
            "Bono East", "Ahafo", "Oti", "Savannah", "North East", "Western North"
        ],
        "lgas": {
            "Greater Accra": ["Accra Metropolitan", "Tema Metropolitan", "Ga South", "Ga East", "Ga West", "Adentan"],
            "Ashanti": ["Kumasi Metropolitan", "Obuasi Municipal", "Ejisu", "Asante Akim South", "Bekwai"],
            "Western": ["Sekondi-Takoradi Municipal", "Tarkwa-Nsuaem", "Prestea-Huni Valley"],
        }
    },
    "United States of America": {
        "state_label": "State",
        "lga_label": "City / County",
        "states": [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
            "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
            "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
            "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
            "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
            "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
        ],
        "lgas": {
            "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Sacramento"],
            "New York": ["New York City", "Buffalo", "Rochester", "Albany", "Syracuse"],
            "Texas": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
            "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee"],
            "Illinois": ["Chicago", "Aurora", "Naperville", "Joliet", "Springfield"],
        }
    },
    "United Kingdom": {
        "state_label": "Country / Region",
        "lga_label": "County / City",
        "states": ["England", "Scotland", "Wales", "Northern Ireland", "Greater London"],
        "lgas": {
            "England": ["Greater London", "West Midlands", "Greater Manchester", "West Yorkshire", "Hampshire"],
            "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee", "Highland"],
            "Wales": ["Cardiff", "Swansea", "Newport", "Wrexham"],
            "Northern Ireland": ["Belfast", "Derry", "Lisburn", "Newry"],
            "Greater London": ["Camden", "Greenwich", "Hackney", "Kensington and Chelsea", "Westminster"],
        }
    },
    "Canada": {
        "state_label": "Province / Territory",
        "lga_label": "City / Municipality",
        "states": [
            "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
            "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan",
            "Northwest Territories", "Nunavut", "Yukon"
        ],
        "lgas": {
            "Ontario": ["Toronto", "Ottawa", "Mississauga", "Brampton", "Hamilton"],
            "Quebec": ["Montreal", "Quebec City", "Laval", "Gatineau", "Longueuil"],
            "British Columbia": ["Vancouver", "Surrey", "Burnaby", "Richmond", "Victoria"],
            "Alberta": ["Calgary", "Edmonton", "Red Deer", "Lethbridge"],
        }
    },
    "Albania": {
        "state_label": "County / County Region",
        "lga_label": "Municipality / City",
        "states": [
            "Tirana", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier",
            "Korçë", "Lezhë", "Berat", "Dibër", "Gjirokastër", "Kukës"
        ],
        "lgas": {
            "Tirana": ["Tirana City", "Kamëz", "Vorë"],
            "Durrës": ["Durrës City", "Shijak", "Krujë"],
            "Vlorë": ["Vlorë City", "Himara", "Sarandë"],
            "Shkodër": ["Shkodër City", "Vau i Dejës", "Malësi e Madhe"],
            "Elbasan": ["Elbasan City", "Cërrik", "Gramsh", "Librazhd"],
            "Fier": ["Fier City", "Lushnjë", "Mallakastër"],
        }
    },
    "Algeria": {
        "state_label": "Province (Wilaya)",
        "lga_label": "District / City",
        "states": ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Batna", "Djelfa", "Sétif", "Sidi Bel Abbès", "Biskra"],
        "lgas": {
            "Algiers": ["Algiers Center", "Bab El Oued", "Casbah", "El Harrach", "Zéralda"],
            "Oran": ["Oran City", "Es Senia", "Bir El Djir"],
        }
    },
    "Angola": {
        "state_label": "Province",
        "lga_label": "Municipality",
        "states": ["Luanda", "Benguela", "Huambo", "Huíla", "Cabinda", "Cuanza Sul", "Malanje"],
        "lgas": {
            "Luanda": ["Luanda City", "Belas", "Cacuaco", "Cazenga", "Viana"],
        }
    },
    "Australia": {
        "state_label": "State / Territory",
        "lga_label": "City / Local Area",
        "states": ["New South Wales", "Victoria", "Queensland", "Western Australia", "South Australia", "Tasmania", "Australian Capital Territory", "Northern Territory"],
        "lgas": {
            "New South Wales": ["Sydney", "Newcastle", "Wollongong", "Central Coast"],
            "Victoria": ["Melbourne", "Geelong", "Ballarat", "Bendigo"],
            "Queensland": ["Brisbane", "Gold Coast", "Sunshine Coast", "Townsville"],
        }
    },
    "Benin": {
        "state_label": "Department / Region",
        "lga_label": "Commune / City",
        "states": ["Littoral (Cotonou)", "Atlantique", "Ouémé", "Borgou", "Zou", "Atakora", "Alibori", "Donga", "Mono", "Couffo", "Collines", "Plateaux"],
        "lgas": {
            "Littoral (Cotonou)": ["Cotonou City", "Akpakpa", "Haie Vive"],
            "Atlantique": ["Abomey-Calavi", "Ouidah", "Allada"],
            "Ouémé": ["Porto-Novo", "Sèmè-Kpodji"],
        }
    },
    "Brazil": {
        "state_label": "State",
        "lga_label": "Municipality / City",
        "states": ["São Paulo", "Rio de Janeiro", "Minas Gerais", "Bahia", "Paraná", "Rio Grande do Sul", "Pernambuco", "Ceará", "Brasília (Distrito Federal)"],
        "lgas": {
            "São Paulo": ["São Paulo City", "Campinas", "Guarulhos", "Santos"],
            "Rio de Janeiro": ["Rio de Janeiro City", "Niterói", "Duque de Caxias"],
        }
    },
    "Cameroon": {
        "state_label": "Region",
        "lga_label": "Department / City",
        "states": ["Centre (Yaoundé)", "Littoral (Douala)", "West", "North-West", "South-West", "Adamawa", "Far North", "North", "East", "South"],
        "lgas": {
            "Centre (Yaoundé)": ["Yaoundé I", "Yaoundé II", "Yaoundé III", "Mfoundi"],
            "Littoral (Douala)": ["Douala I", "Douala II", "Douala III", "Wouri"],
        }
    },
    "Egypt": {
        "state_label": "Governorate",
        "lga_label": "City / District",
        "states": ["Cairo", "Alexandria", "Giza", "Dakahlia", "Red Sea", "Sharqia", "Beheira", "Gharbia", "Asyut", "Suez"],
        "lgas": {
            "Cairo": ["New Cairo", "Maadi", "Heliopolis", "Nasr City", "Zamalek"],
            "Alexandria": ["Alexandria City", "El Montaza", "Borg El Arab"],
        }
    },
    "France": {
        "state_label": "Region / Department",
        "lga_label": "City / Commune",
        "states": ["Île-de-France (Paris)", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine", "Occitanie", "Hauts-de-France", "Provence-Alpes-Côte d'Azur", "Grand Est"],
        "lgas": {
            "Île-de-France (Paris)": ["Paris", "Boulogne-Billancourt", "Saint-Denis", "Versailles", "Nanterre"],
            "Provence-Alpes-Côte d'Azur": ["Marseille", "Nice", "Toulon", "Aix-en-Provence"],
        }
    },
    "Germany": {
        "state_label": "State (Bundesland)",
        "lga_label": "City / District",
        "states": ["Bavaria", "North Rhine-Westphalia", "Baden-Württemberg", "Lower Saxony", "Hesse", "Berlin", "Saxony", "Hamburg"],
        "lgas": {
            "Bavaria": ["Munich", "Nuremberg", "Augsburg", "Regensburg"],
            "North Rhine-Westphalia": ["Cologne", "Düsseldorf", "Dortmund", "Essen"],
            "Berlin": ["Berlin City", "Mitte", "Pankow", "Charlottenburg"],
        }
    },
    "India": {
        "state_label": "State / Union Territory",
        "lga_label": "District / City",
        "states": ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "West Bengal", "Gujarat", "Telangana", "Kerala", "Punjab"],
        "lgas": {
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane"],
            "Delhi": ["New Delhi", "North Delhi", "South Delhi"],
            "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru"],
        }
    },
    "Japan": {
        "state_label": "Prefecture",
        "lga_label": "City / Ward",
        "states": ["Tokyo", "Osaka", "Kanagawa", "Aichi", "Hokkaido", "Kyoto", "Fukuoka", "Hyogo", "Saitama"],
        "lgas": {
            "Tokyo": ["Shinjuku", "Shibuya", "Chiyoda", "Minato", "Setagaya"],
            "Osaka": ["Osaka City", "Sakai", "Higashiosaka"],
        }
    },
    "Kenya": {
        "state_label": "County",
        "lga_label": "Sub-County / City",
        "states": [
            "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Kiambu", "Machakos", "Uasin Gishu", "Kilifi", "Kajiado", "Kakamega"
        ],
        "lgas": {
            "Nairobi": ["Westlands", "Dagoretti", "Langata", "Kibarani", "Kasarani", "Embakasi"],
            "Mombasa": ["Changamwe", "Jomvu", "Kisauni", "Nyali", "Likoni", "Mvita"],
        }
    },
    "Mexico": {
        "state_label": "State",
        "lga_label": "Municipality / City",
        "states": ["Mexico City", "Jalisco", "Nuevo León", "State of Mexico", "Puebla", "Guanajuato", "Yucatán", "Quintana Roo"],
        "lgas": {
            "Mexico City": ["Cuauhtémoc", "Coyoacán", "Polanco", "Iztapalapa"],
            "Jalisco": ["Guadalajara", "Zapopan", "Puerto Vallarta"],
        }
    },
    "Morocco": {
        "state_label": "Region",
        "lga_label": "Province / City",
        "states": ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakesh-Safi", "Tangier-Tetouan-Al Hoceima", "Fès-Meknès", "Souss-Massa"],
        "lgas": {
            "Casablanca-Settat": ["Casablanca", "Mohammedia", "El Jadida"],
            "Rabat-Salé-Kénitra": ["Rabat", "Salé", "Kénitra"],
        }
    },
    "Netherlands": {
        "state_label": "Province",
        "lga_label": "Municipality / City",
        "states": ["North Holland", "South Holland", "Utrecht", "North Brabant", "Gelderland", "Overijssel"],
        "lgas": {
            "North Holland": ["Amsterdam", "Haarlem", "Zaanstad", "Alkmaar"],
            "South Holland": ["Rotterdam", "The Hague", "Leiden", "Delft"],
        }
    },
    "Rwanda": {
        "state_label": "Province",
        "lga_label": "District / City",
        "states": ["Kigali", "Eastern Province", "Southern Province", "Western Province", "Northern Province"],
        "lgas": {
            "Kigali": ["Nyarugenge", "Gasabo", "Kicukiro"],
        }
    },
    "Saudi Arabia": {
        "state_label": "Region / Province",
        "lga_label": "City / Governorate",
        "states": ["Riyadh", "Makkah", "Eastern Province", "Madinah", "Asir", "Tabuk"],
        "lgas": {
            "Riyadh": ["Riyadh City", "Al Kharj", "Diriyah"],
            "Makkah": ["Jeddah", "Makkah City", "Taif"],
        }
    },
    "Senegal": {
        "state_label": "Region",
        "lga_label": "Department / City",
        "states": ["Dakar", "Thiès", "Saint-Louis", "Kaolack", "Ziguinchor", "Diourbel", "Louga"],
        "lgas": {
            "Dakar": ["Dakar City", "Guédiawaye", "Pikine", "Rufisque"],
        }
    },
    "South Africa": {
        "state_label": "Province",
        "lga_label": "Municipality / City",
        "states": [
            "Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape", "Free State", "Limpopo", "Mpumalanga", "North West", "Northern Cape"
        ],
        "lgas": {
            "KwaZulu-Natal": ["eThekwini (Durban)", "Msunduzi (Pietermaritzburg)"],
            "Gauteng": ["Johannesburg", "Tshwane (Pretoria)", "Ekurhuleni"],
            "Western Cape": ["City of Cape Town", "George", "Stellenbosch"],
        }
    },
    "Spain": {
        "state_label": "Autonomous Community",
        "lga_label": "Province / City",
        "states": ["Madrid", "Catalonia", "Andalusia", "Valencia", "Galicia", "Basque Country"],
        "lgas": {
            "Madrid": ["Madrid City", "Alcalá de Henares", "Getafe", "Leganés"],
            "Catalonia": ["Barcelona", "Girona", "Lleida", "Tarragona"],
        }
    },
    "Tanzania": {
        "state_label": "Region",
        "lga_label": "District / City",
        "states": ["Dar es Salaam", "Dodoma", "Mwanza", "Arusha", "Zanzibar", "Kilimanjaro", "Tanga"],
        "lgas": {
            "Dar es Salaam": ["Ilala", "Kinondoni", "Temeke", "Ubungo"],
        }
    },
    "Turkey": {
        "state_label": "Province",
        "lga_label": "District / City",
        "states": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya"],
        "lgas": {
            "Istanbul": ["Karaköy", "Beşiktaş", "Kadıköy", "Şişli", "Üsküdar"],
            "Ankara": ["Çankaya", "Keçiören", "Yenimahalle"],
        }
    },
    "Uganda": {
        "state_label": "Region / District",
        "lga_label": "Sub-County / City",
        "states": ["Central (Kampala)", "Western", "Eastern", "Northern", "Wakiso", "Mukono", "Jinja"],
        "lgas": {
            "Central (Kampala)": ["Kampala Central", "Kawempe", "Makindye", "Nakawa", "Rubaga"],
        }
    },
    "United Arab Emirates": {
        "state_label": "Emirate",
        "lga_label": "City / Area",
        "states": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"],
        "lgas": {
            "Dubai": ["Downtown Dubai", "Dubai Marina", "Jumeirah", "Deira", "Business Bay"],
            "Abu Dhabi": ["Abu Dhabi City", "Al Ain", "Yas Island"],
        }
    }
}

COUNTRIES_BY_CONTINENT = {
    "Africa": [
        "Nigeria", "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso",
        "Burundi", "Cabo Verde", "Cameroon", "Central African Republic",
        "Chad", "Comoros", "Congo (Brazzaville)", "Congo (Kinshasa)",
        "Côte d'Ivoire", "Djibouti", "Egypt", "Equatorial Guinea",
        "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana",
        "Guinea", "Guinea-Bissau", "Kenya", "Lesotho", "Liberia",
        "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius",
        "Morocco", "Mozambique", "Namibia", "Niger", "Rwanda",
        "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone",
        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania",
        "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe",
    ],
    "Europe": [
        "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina",
        "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia",
        "Finland", "France", "Germany", "Greece", "Hungary", "Iceland",
        "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania",
        "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro",
        "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal",
        "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia",
        "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom",
        "Vatican City",
    ],
    "Asia": [
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh",
        "Bhutan", "Brunei", "Cambodia", "China", "Georgia", "India",
        "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan",
        "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon",
        "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal",
        "North Korea", "Oman", "Pakistan", "Palestine", "Philippines",
        "Qatar", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka",
        "Syria", "Taiwan", "Tajikistan", "Thailand", "Timor-Leste",
        "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan",
        "Vietnam", "Yemen",
    ],
    "North America": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada",
        "Costa Rica", "Cuba", "Dominica", "Dominican Republic",
        "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras",
        "Jamaica", "Mexico", "Nicaragua", "Panama",
        "Saint Kitts and Nevis", "Saint Lucia",
        "Saint Vincent and the Grenadines", "Trinidad and Tobago",
        "United States of America",
    ],
    "South America": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
        "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela",
    ],
    "Oceania": [
        "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia",
        "Nauru", "New Zealand", "Palau", "Papua New Guinea",
        "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu",
    ],
}

DEFAULT_COUNTRY = "Nigeria"
