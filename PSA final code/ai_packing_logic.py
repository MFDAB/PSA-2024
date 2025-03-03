from datetime import datetime
from multiprocessing import Pool, Manager, cpu_count
from py3dbp import Packer, Bin, Item

# Filter cargo to match containers by origin, destination, and departure date


def filter_compatible(cargo, bin_volume):
    # Access the metadata stored in the Bin object
    bin_metadata = bin_volume.metadata

    # Parse the date strings into datetime objects
    cargo_date = datetime.fromisoformat(cargo['departure_date'])
    bin_date = datetime.fromisoformat(bin_metadata['departure_date'])

    # Calculate the difference in days
    date_diff = abs((cargo_date - bin_date).days)

    # Return True if the cargo matches the bin based on origin, destination, and flexidate
    return (
        cargo['origin'] == bin_metadata['origin'] and
        cargo['destination'] == bin_metadata['destination'] and
        date_diff <= bin_metadata['flexidate']
    )


# Create shared containers (bins) with multiprocessing support


def create_bins(manager, containers):
    bins = manager.list()  # Create a shared list for multiprocessing

    for container in containers:
        bin_volume = Bin(
            container['container_id'],
            container['width'],
            container['height'],
            container['depth'],
            1000  # Arbitrary high max weight
        )

        # Store container metadata inside the Bin object
        bin_volume.metadata = {
            'container_id': container['container_id'],
            'origin': container['origin'],
            'destination': container['destination'],
            'departure_date': container['departure_date'],
            'flexidate': container['flexidate']
        }

        bins.append(bin_volume)

    return bins


# Assign cargo to bins and pack them


def add_items_and_pack(chunk, shared_bins, lock):
    packer = Packer()
    for bin_volume in shared_bins:
        packer.add_bin(bin_volume)
    for cargo in chunk:
        item = Item(
            cargo['cargo_id'],
            cargo['width'],
            cargo['height'],
            cargo['depth'],
            10  # Arbitrary weight
        )
        packer.add_item(item)
    with lock:
        packer.pack()
    return


def parallel_pack(cargo_list, containers, num_processes):
    manager = Manager()
    lock = manager.Lock()
    shared_bins = create_bins(manager, containers)

    # Track all cargo that gets packed and any unmatched cargo
    packed_dict = {bin_volume.metadata['container_id']: []
                   for bin_volume in shared_bins}
    unmatched_cargo = []

    # Filter and assign cargo to appropriate bins
    def assign_cargo(cargo):
        assigned = False
        for bin_volume in shared_bins:
            if filter_compatible(cargo, bin_volume):
                # Add the cargo to this bin's list
                packed_dict[bin_volume.metadata['container_id']].append(
                    cargo['cargo_id'])
                assigned = True
                break
        if not assigned:
            unmatched_cargo.append(cargo)

    # Assign all cargo
    for cargo in cargo_list:
        assign_cargo(cargo)

    # Handle any unmatched cargo by adding it to the first available bin
    if unmatched_cargo:
        first_bin = shared_bins[0]
        for cargo in unmatched_cargo:
            packed_dict[first_bin.metadata['container_id']].append(
                cargo['cargo_id'])

    return packed_dict
