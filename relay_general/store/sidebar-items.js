initSidebarItems({"enum":[["BreakdownConfig","Configuration to define breakdown to be generated based on properties and breakdown type."]],"fn":[["compute_measurements","Compute additional measurements derived from existing ones."],["get_breakdown_measurements",""],["get_measurement","Get the value for a measurement, e.g. lcp -> event.measurements.lcp"],["get_transaction_op",""],["is_high_cardinality_sdk","List of SDKs which we assume to produce high cardinality transaction names, such as “/user/123134/login”. Newer SDK send the [`TransactionSource`] attribute, which we can rely on to determine cardinality, but for old SDKs, we fall back to this list."],["is_valid_platform",""],["light_normalize_event",""],["normalize_dist",""],["validate_timestamps","Returns start and end timestamps if they are both set and start <= end."],["validate_transaction",""]],"struct":[["BreakdownsConfig","Represents the breakdown configuration for a project. Generate a named (key) breakdown (value)."],["ClockDriftProcessor","Corrects clock drift based on the sender’s and receivers timestamps."],["GeoIpLookup","A geo ip lookup helper based on maxmind db files."],["LightNormalizationConfig",""],["SpanOperationsConfig","Configuration to define breakdowns based on span operation name."],["StoreConfig","The config for store."],["StoreProcessor","The processor that normalizes events for store."]],"type":[["GeoIpError","An error in the `GeoIpLookup`."]]});