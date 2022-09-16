%lang starknet

from entry.structs import Checkpoint, Entry, Pair, Currency

namespace EmpiricAggregationModes {
    const MEDIAN = 120282243752302;  // str_to_felt("median")
}

@contract_interface
namespace IOracle {
    func initializer(
        proxy_admin: felt,
        publisher_registry_address: felt,
        currencies_len: felt,
        currencies: Currency*,
        pairs_len: felt,
        pairs: Pair*,
    ) {
    }
    //
    // Getters
    //

    func get_decimals(pair_id: felt) -> (decimals: felt) {
    }

    func get_entries(pair_id: felt, sources_len: felt, sources: felt*) -> (
        entries_len: felt, entries: Entry*
    ) {
    }

    func get_entry(pair_id: felt, source: felt) -> (entry: Entry) {
    }

    func get_value(pair_id: felt, aggregation_mode: felt) -> (
        value: felt, decimals: felt, last_updated_timestamp: felt, num_sources_aggregated: felt
    ) {
    }

    // TODO (rlkelly): add adapters for currency conversion
    // func get_value_with_hops(
    //     currency_ids_len : felt, currency_ids : felt*, aggregation_mode : felt
    // ) -> (
    //     value : felt, decimals : felt, last_updated_timestamp : felt, num_sources_aggregated : felt
    // ):
    // end

    // func get_value_with_USD_hop(
    //     base_currency_id : felt, quote_currency_id : felt, aggregation_mode : felt
    // ) -> (
    //     value : felt, decimals : felt, last_updated_timestamp : felt, num_sources_aggregated : felt
    // ):
    // end

    func get_value_for_sources(
        pair_id: felt, aggregation_mode: felt, sources_len: felt, sources: felt*
    ) -> (value: felt, decimals: felt, last_updated_timestamp: felt, num_sources_aggregated: felt) {
    }

    func get_admin_address() -> (admin_address: felt) {
    }

    func get_publisher_registry_address() -> (publisher_registry_address: felt) {
    }

    func get_latest_checkpoint_index(key: felt) -> (latest: felt) {
    }

    func get_checkpoint(key: felt, index: felt) -> (checkpoint: Checkpoint) {
    }

    func get_sources_threshold() -> (threshold: felt) {
    }

    //
    // Setters
    //

    func publish_entry(new_entry: Entry) {
    }

    func publish_entries(new_entries_len: felt, new_entries: Entry*) {
    }

    func set_admin_address(new_admin_address: felt) {
    }

    func update_publisher_registry_address(publisher_registry_address: felt) {
    }

    func add_currency(currency: Currency) {
    }

    func update_currency(currency: Currency) {
    }

    func add_pair(pair: Pair) {
    }

    func set_checkpoint(key: felt, aggregation_mode: felt) {
    }

    func set_sources_threshold(threshold: felt) {
    }
}