%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin

from contracts.entry.library import Entry
from contracts.oracle.library import (
    Oracle_set_oracle_decimals, Oracle_submit_entry, Oracle_get_entries_for_asset, Oracle_get_price)
from contracts.publisher.registration_library import (
    Publisher_Registration_rotate_key, Publisher_Registration_initialize_key)
from contracts.publisher.library import (
    Publisher_register_publisher, Publisher_get_publisher_public_key)

const DECIMALS = 10

@constructor
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        publisher_registration_key : felt):
    Oracle_set_oracle_decimals(DECIMALS)
    Publisher_Registration_initialize_key(publisher_registration_key)
    return ()
end

#
# Publisher
#

@external
func rotate_publisher_registration_key{
        syscall_ptr : felt*, ecdsa_ptr : SignatureBuiltin*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(old_key : felt, new_key : felt, signature_r : felt, signature_s : felt):
    Publisher_Registration_rotate_key(old_key, new_key, signature_r, signature_s)
    return ()
end

@external
func register_publisher{
        syscall_ptr : felt*, ecdsa_ptr : SignatureBuiltin*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(
        publisher_public_key : felt, publisher : felt, publisher_signature_r : felt,
        publisher_signature_s : felt, registration_signature_r : felt,
        registration_signature_s : felt):
    Publisher_register_publisher(
        publisher_public_key,
        publisher,
        publisher_signature_r,
        publisher_signature_s,
        registration_signature_r,
        registration_signature_s)
    return ()
end

@view
func get_publisher_public_key{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        publisher : felt) -> (publisher_public_key : felt):
    let (publisher_public_key) = Publisher_get_publisher_public_key(publisher)
    return (publisher_public_key)
end

#
# Oracle
#

@external
func submit_entry{
        syscall_ptr : felt*, ecdsa_ptr : SignatureBuiltin*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(new_entry : Entry, signature_r : felt, signature_s : felt):
    Oracle_submit_entry(new_entry, signature_r, signature_s)
    return ()
end

@view
func get_entries_for_asset{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        asset : felt) -> (entries_len : felt, entries : Entry*):
    let (entries_len, entries) = Oracle_get_entries_for_asset(asset)
    return (entries_len, entries)
end

@view
func get_price{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(asset : felt) -> (
        price : felt):
    let (price) = Oracle_get_price(asset)
    return (price)
end