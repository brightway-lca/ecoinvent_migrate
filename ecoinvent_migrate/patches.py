TECHNOSPHERE_PATCHES = {
    ("3.9.1", "3.10"): {
        'replace': [
            {
                'source': {
                    'name': "modified Solvay process, Hou's process",
                    'location': 'GLO',
                    'reference product': 'ammonium chloride',
                    'unit': 'kg'
                },
                'target': {
                    'name': "soda ash production, dense, Hou's process",
                    'location': 'GLO',
                    'reference product': 'ammonium chloride',
                    'unit': 'kg'
                }
            },
            {
                'source': {
                    'name': 'Mannheim process',
                    'location': 'RER',
                    'reference product': 'sodium sulfate, anhydrite',
                    'unit': 'kg'
                },
                'target': {
                    'name': "hydrochloric acid production, Mannheim process",
                    'location': 'RER',
                    'reference product': 'sodium sulfate, anhydrite',
                    'unit': 'kg'
                }
            },
            {
                'source': {
                    'name': 'Mannheim process',
                    'location': 'RoW',
                    'reference product': 'sodium sulfate, anhydrite',
                    'unit': 'kg'
                },
                'target': {
                    'name': "hydrochloric acid production, Mannheim process",
                    'location': 'RoW',
                    'reference product': 'sodium sulfate, anhydrite',
                    'unit': 'kg'
                }
            },
        ]
    }
}
