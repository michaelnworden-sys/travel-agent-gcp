# knowledge.py

# This dictionary contains the "Local Knowledge" for every terminal town.
# It includes the pre-written description (Mike's "Canned Answer") and the
# search rules for the Google Places API.

TERMINAL_DATA = {
    "Seattle": {
        "description": "Colman Dock puts you at the heart of Seattle's vibrant waterfront scene. Pike Place Market, the Seattle Aquarium, and the iconic Great Wheel all lie within easy walking distance. Stroll the bustling piers filled with shops and restaurants, or venture into historic Pioneer Square to explore the city's roots.",
        "coordinates": { "latitude": 47.6019, "longitude": -122.3374 },
        "searchRadius": 3000,
        "notesForGemini": "Prioritize proximity to the Colman Dock terminal. Results MUST be in Seattle."
    },
    "Bainbridge Island": {
        "description": "The Bainbridge Island terminal drops you right into Winslow's downtown district, perfect for exploring on foot. Local highlights include waterfront dining, unique boutiques, and art galleries. The island's rolling hills and waterfront roads make it popular with cyclists, and several award-winning wineries offer tastings throughout the island.",
        "coordinates": { "latitude": 47.6231, "longitude": -122.5126 },
        "searchRadius": 3000,
        "notesForGemini": "You can ONLY return results for Bainbridge Island, Poulsbo and Suquamish areas. Ignore Seattle results, they do not count."
    },
    "Bremerton": {
        "description": "Bremerton's waterfront and Harborside district welcome you with walkable streets and maritime heritage. Tour the historic USS Turner Joy or explore the Navy Museum, both steps from the dock. The downtown Arts District and scenic boardwalk offer perfect spots to soak in harbor views.",
        "coordinates": { "latitude": 47.5630, "longitude": -122.6241 },
        "searchRadius": 3000,
        "notesForGemini": "Results must be in the city of Bremerton. Do NOT include Port Orchard addresses. Olympic Peninsula attractions are relevant."
    },
    "Kingston": {
        "description": "Kingston's delightful main street bustles with local boutiques, bookstores, and popular spots like the Kingston Ale House. Choose from everything from pizza to poke bowls, then relax by the marina with a coffee while planning your next adventure.",
        "coordinates": { "latitude": 47.7966, "longitude": -122.4966 },
        "searchRadius": 3000,
        "notesForGemini": "Results should be in the city of Kingston or westward on the mainland. Do NOT include anything east of Puget Sound."
    },
    "Edmonds": {
        "description": "Edmonds combines vibrant waterfront energy with small-town charm. Brackett's Landing park offers immediate beach access and stunning Salish Sea views right next to the terminal. Downtown streets showcase unique boutiques, art galleries, and diverse restaurants all within easy walking distance.",
        "coordinates": { "latitude": 47.8118, "longitude": -122.3831 },
        "searchRadius": 3000,
        "notesForGemini": "Results should be in Edmonds or eastward from the terminal on the mainland."
    },
    "Vashon": {
        "description": "Vashon Island's northern dock sits about 5 miles from the main town center, so plan for onward travel by car, bike, or bus to explore the island's artsy communities and rural charm. A local cafe and market provide immediate convenience right at the terminal.",
        "coordinates": { "latitude": 47.5146, "longitude": -122.4646 },
        "searchRadius": 12000,
        "notesForGemini": "All results must be located on Vashon Island only. Ignonre results that do not have a Vashon address."
    },
    "Tahlequah": {
        "description": "Tahlequah occupies Vashon Island's scenic southern tip, connecting to Point Defiance. While this residential area offers limited amenities directly at the dock, it provides a peaceful launching point for exploring the island's main villages and attractions with your own transportation.",
        "coordinates": { "latitude": 47.3364, "longitude": -122.5085 },
        "searchRadius": 12000,
        "notesForGemini": "Ensure all results are located on Vashon Island only. Do not include Tacoma or mainland locations."
    },
    "Point Defiance": {
        "description": "Point Defiance Park surrounds the terminal with 760 acres of urban wilderness in Tacoma. Discover the world-class Point Defiance Zoo & Aquarium, hike miles of scenic trails, or relax on stunning beaches. This magnificent park creates a destination worth visiting on its own.",
        "coordinates": { "latitude": 47.3101, "longitude": -122.5029 },
        "searchRadius": 5000,
        "notesForGemini": "Focus on Point Defiance Park area attractions first, then broader Tacoma area. Do not include Vashon Island locations."
    },
    "Mukilteo": {
        "description": "The Mukilteo ferry terminal sits adjacent to the charming Lighthouse Park, offering beautiful Salish Sea vistas. You can stroll the beach, visit the historic wooden lighthouse, and watch ferries glide by. Classic Northwest seafood at Ivar's and local brews at Diamond Knot are right near the dock.",
        "coordinates": { "latitude": 47.9484, "longitude": -122.3027 },
        "searchRadius": 12000,
        "notesForGemini": "Results should be on the mainland, in Mukilteo or Everett. Do NOT include Whidbey Island or Clinton."
    },
    "Clinton": {
        "description": "Clinton welcomes you to southern Whidbey Island with nearby coffee spots, casual eateries, and unique shops perfect for a quick stop. From here, explore the rest of Whidbey's stunning beaches, working farms, and thriving artisan communities.",
        "coordinates": { "latitude": 47.9778, "longitude": -122.3551 },
        "searchRadius": 12000,
        "notesForGemini": "Only list results on Whidbey Island. For immediate needs (coffee, food, auto repair), prioritize locations closer to the Clinton terminal. Attractions can be island-wide."
    },
    "Coupeville": {
        "description": "Coupeville's terminal neighbors Fort Casey State Park, where you can explore historic coastal defense batteries, climb the lighthouse, and enjoy camping facilities. The charming town of Coupeville itself, with its shops and restaurants, requires a scenic drive several miles from the terminal.",
        "coordinates": { "latitude": 48.1706, "longitude": -122.6841 },
        "searchRadius": 15000,
        "notesForGemini": "Only list results on Whidbey Island. Emphasize Fort Casey for immediate attractions. For the town of Coupeville, mention it requires travel from the terminal."
    },
    "Port Townsend": {
        "description": "Port Townsend is a historic Victorian seaport town on the Olympic Peninsula, well-known for its charming downtown. The ferry docks close to the heart of the town, making it easy to walk to unique shops, art galleries, diverse restaurants, and explore its rich maritime history and beautifully preserved architecture.",
        "coordinates": { "latitude": 48.1130, "longitude": -122.7562 },
        "searchRadius": 10000,
        "notesForGemini": "Focus on Port Townsend city attractions and walkable downtown area. Olympic Peninsula attractions are also relevant."
    },
    "Southworth": {
        "description": "Southworth connects you to the Kitsap Peninsula from a beautiful wooded setting. While dock amenities center around Southworth Grocery, this peaceful terminal serves as your launching point for scenic Peninsula drives and kayaking adventures.",
        "coordinates": { "latitude": 47.5126, "longitude": -122.5000 },
        "searchRadius": 25000,
        "specialMessage": "Services near the Southworth terminal are very limited. I'll search in Southworth and nearby mainland areas like Port Orchard, Bethel, Parkwood, and Gorst. Attractions on the Olympic Peninsula might also be relevant depending on your query.",
        "notesForGemini": "User has been informed of limited services. Search results can include Southworth, Port Orchard, Bethel, Parkwood, and Gorst. Do NOT include Vashon Island. For attractions, Olympic Peninsula is okay; consider mentioning distance. Emphasize limited local services for needs."
    },
    "Fauntleroy": {
        "description": "Fauntleroy offers West Seattle's hidden gem experience. Lincoln Park sprawls just north of the terminal, where you can hike wooded trails that lead to stunning Puget Sound beaches and tide pools. Walk a few blocks inland to find the charming Endolyne business district, home to cozy neighborhood cafes, local pubs, and family-owned restaurants. This quieter corner of West Seattle provides a peaceful escape with easy access to both nature and neighborhood charm.",
        "coordinates": { "latitude": 47.5230, "longitude": -122.3941 },
        "searchRadius": 5000,
        "notesForGemini": "Prioritize results in West Seattle, considering areas eastward and southward from the terminal. Do not list Vashon island results."
    },
    "Anacortes": {
        "description": "Anacortes is your mainland gateway to the San Juan Islands. Before you even board the ferry, you can explore the city's historic downtown, filled with unique shops, art galleries, and diverse restaurants. With beautiful marina views and nearby parks, it's a wonderful destination in its own right.",
        "coordinates": { "latitude": 48.5133, "longitude": -122.6120 },
        "searchRadius": 5000,
        "notesForGemini": "Focus on Anacortes city attractions and downtown area. Do not include any San Juan Islands results."
    },
    "Friday Harbor": {
        "description": "Friday Harbor is the bustling heart of San Juan Island. It's a charming, walkable town right where the ferry docks, filled with restaurants, boutiques, and the Whale Museum. Friday Harbor serves as your starting point for exploring the rest of the island, from Lime Kiln Point to the historic English and American Camps.",
        "coordinates": { "latitude": 48.5350, "longitude": -123.0163 },
        "searchCenterCoordinates": { "latitude": 48.540543, "longitude": -123.094837 },
        "searchRadius": 12000,
        "notesForGemini": "You may Only list results located on San Juan Island. Do NOT include results from any other San Juan Islands (Orcas, Lopez, Shaw)."
    },
    "Orcas Island": {
        "description": "Orcas Island's dramatic horseshoe shape and soaring Mount Constitution create an unforgettable backdrop for outdoor adventures. The terminal is located 8 miles south of Eastsound, so plan for transportation to reach the island's artisan community, hiking trails, and panoramic viewpoints.",
        "coordinates": { "latitude": 48.5912, "longitude": -122.9048 },
        "searchCenterCoordinates": { "latitude": 48.653813, "longitude": -122.901323 },
        "searchRadius": 15000,
        "notesForGemini": "Only list results located on Orcas Island. Do NOT include results from other San Juan Islands (Friday Harbor, Lopez, Shaw)."
    },
    "Lopez Island": {
        "description": "Lopez Island is known as the 'Friendly Isle' for its gentle pace. The ferry dock is a few miles from Lopez Village, the island's commercial hub, so you will need a car or bike to get around. With its rolling hills and scenic roads, Lopez is considered a cyclist's paradise. The village offers charming cafes, galleries, and a bakery.",
        "coordinates": { "latitude": 48.5447, "longitude": -122.9150 },
        "searchCenterCoordinates": { "latitude": 48.497151, "longitude": -122.898710 },
        "searchRadius": 10000,
        "notesForGemini": "You may Only list results located on Lopez Island. Do NOT include results from other San Juan Islands (Friday Harbor, Orcas, Shaw)."
    },
    "Shaw Island": {
        "description": "Shaw Island is the smallest and most tranquil of the ferry-served San Juan Islands. You should be aware that commercial services here are very limited. The island's main point of interest, the historic Shaw General Store, is located right at the ferry landing. Shaw is a place for quiet scenic drives and enjoying the simple beauty of island life.",
        "coordinates": { "latitude": 48.5670, "longitude": -122.9463 },
        "specialCases": {
            "restaurant, food, breakfast, lunch, dinner, cafe": {
                "customMessage": "Services on Shaw Island are very limited. The historic Shaw General Store, located right at the ferry dock, has a small cafe and deli with groceries and prepared foods."
            },
            "hotel, lodging, stay, inn, motel": {
                 "customMessage": "There are no hotels or public lodging facilities on Shaw Island."
            }
        },
        "notesForGemini": "Results should be on Shaw Island only, but emphasize that commercial services are very limited. Shaw General Store is the main attraction."
    }
}