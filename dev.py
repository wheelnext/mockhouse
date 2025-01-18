VARIANTS_2_GENERATE = {
    # ************************ DEVELOPER NOTE ************************ #
    # The idea here is to provide "different architectures" which sometimes have
    # overlapping key/ sometimes they don't. Not all architectures necessarily make
    # sense to publish all "key/val". The point is most likely to inject all kind of
    # weird cases that later `mockhouse` will be able to serve and PIP + Plugin can do
    # its thing
    #
    # Author's Note: Humor is absolutely an integral piece of this PEP.
    #
    # ************************ DEVELOPER NOTE ************************ #
    # "fictional_hw": [{
    #     "architecture": "*",
    #     "compute_capability": ">1",
    #     "compute_accuracy": ">1",
    #     "humor": ">1"
    # }],
    "fictional_hw": [
        {
            "architecture": "deepthought",
            "compute_capability": 10,  # It knows the ultimate answer to life, the
            # universe, and everything!
            "compute_accuracy": 10,  # It knows the ultimate answer to life, the
            # universe, and everything! Humor is obviously undefined for deepthought.
        },
        {
            "architecture": "tars",
            "compute_capability": 8,  # Handles complex space missions and emotional AI
            # interactions.
            "compute_accuracy": 8,  # Can get you through a black hole, but don't push
            # the humor settings too high!
            "humor": 10,  # Adjustable humor settings from deadpan to hilarious
        },
        {
            "architecture": "HAL9000",
            "compute_capability": 6,  # Extremely reliable until it starts to question
            # human commands ...
            # `compute_accuracy` is obviously undefined for HAL9000 since it questions
            # Human commands.
            "humor": 2,  # A bit of a cold operator, though it tries to be polite.
        },
        {
            "architecture": "mother",
            "compute_capability": 4,  # Efficient at monitoring and mission control -
            # not ground shaking
            # `compute_accuracy` is obviously undefined for mother -- the concept does
            # not make sense
            # `humor` is obviously undefined for mother (No jokes, just facts.) -- the
            # concept does not make sense
        },
    ],
    # "fictional_tech": [{
    #     "technology": "*",
    #     "risk_min_tolerance": ">0, <=10,000",
    #     "quantum_capability": in [
    #       NEWTONIAN, SIMPLE_SUPERPOSITION, QUANTUM_SUPERFLUID , QUANTUM_FOAM
    #     ],
    #     "power_requirements_in_solar_output": ">0.0, <1.0"
    # }]
    "fictional_tech": [
        {
            "technology": "Auto Chef and Food Replicator",  # The Fifth Element
            "risk_min_tolerance": 50,  # Unless it malfunctions, you'll be eating well.
            "quantum_capability": "SIMPLE_SUPERPOSITION",  # It uses basic quantum
            # principles to combine ingredients and create meals, but the tech
            # doesn't push the boundaries of quantum mechanics.
            "power_requirements_in_solar_output": 0.00001,  # Fairly simple process
        },
        {
            "technology": "Infinite Improbability Drive",  # Hitchhiker's Guide
            "risk_min_tolerance": 10000,  # Turning people into sofas or releasing
            # sentient whales mid-flight is always a possibility.
            "quantum_capability": "QUANTUM_FOAM",  # The drive taps into the quantum
            # fluctuations of the universe, creating random, unpredictable effects by
            # distorting reality. It's beyond comprehension and controlled chaos on a
            # cosmic scale.
            "power_requirements_in_solar_output": 0.6,  # The drive requires extreme
            # energy to distort probabilities and alter the fabric of reality, much
            # like creating temporary wormholes or impossibly improbable events.
        },
    ],
}

if __name__ == "__main__":
    from collections import defaultdict

    # # Split the top list of variants into a dict of variants per provider
    # variants_by_provider_dict = defaultdict(list)

    # for item in VARIANTS_2_GENERATE:
    #     for key, value in item.items():
    #         variants_by_provider_dict[key].append(value)

    # pprint(VARIANTS_2_GENERATE, indent=4)

    # # Initialize a defaultdict to hold the metadata grouped by their top-lvl keys
    variants_metadata_by_provider_dict = defaultdict(list)

    for provider, provider_variants in VARIANTS_2_GENERATE.items():
        for variant in provider_variants:
            build_metadata = []
            for key, val in variant.items():
                build_metadata.append(
                    f"{provider.upper()} :: {key.upper()} :: {str(val).upper()}"
                )
            variants_metadata_by_provider_dict[provider].append(build_metadata)

    # pprint(variants_metadata_by_provider_dict)
    # print(dict(variants_metadata_by_provider_dict))
    import itertools
    # Get all the keys in the dictionary
    # keys = list(variants_metadata_by_provider_dict.keys())

    # # Iterate over all possible combinations of items from the lists of different keys
    # combinations = [
    #     sum(key_pair, [])
    #     for key_pair in product(
    #         *[variants_metadata_by_provider_dict[key] for key in keys]
    #     )
    # ]

    # # Also, add combinations where only one of the lists is included
    # for key in keys:
    #     for item in variants_metadata_by_provider_dict[key]:
    #         combinations.append(item.copy())
    def generate_combination(data_input: dict):
        provider_meta_dict = defaultdict(list)

        # Extract the 'values' from the data, preserving order
        for provider, provider_variants in data_input.items():
            for variant in provider_variants:
                build_meta = []
                for key, val in variant.items():
                    build_meta.append(
                        f"{provider.upper()} :: {key.upper()} :: {str(val).upper()}"
                    )
                provider_meta_dict[provider].append(build_meta)

            # Generate all possible combinations, including the case of providers
            # appearing independently
            for provider_combinations in provider_meta_dict.values():
                # Yield each provider's key-value pairs independently first
                for combination in provider_combinations:
                    yield sorted(combination)

            # Now generate combinations across providers' key-value pairs
            for product in itertools.product(*provider_meta_dict.values()):
                # Combine all combinations into a single list
                combined = [item for sublist in product for item in sublist]
                yield sorted(combined)

    from pprint import pprint

    # Print the resulting combinations
    for combo in generate_combination(VARIANTS_2_GENERATE):
        pprint(combo)
        print()
