import { ec, BNInput } from 'elliptic';

/**
 * @module Serialize
 */

/** A field in an abi */
interface Field {
    /** Field name */
    name: string;
    /** Type name in string form */
    typeName: string;
    /** Type of the field */
    type?: Type;
}
/** Options for serialize() and deserialize() */
interface SerializerOptions {
    bytesAsUint8Array?: boolean;
}
/** State for serialize() and deserialize() */
declare class SerializerState {
    options: SerializerOptions;
    /** Have any binary extensions been skipped? */
    skippedBinaryExtension: boolean;
    constructor(options?: SerializerOptions);
}
/**
 * An Anyvar (non-short form) may be any of the following:
 *  * null
 *  * string
 *  * number
 *    * Caution: assumes number is int32. Use {type, value} form for other numeric types
 *  * an array of anyvar
 *  * {type, value}
 *      * type is a string matching one of the predefined types in anyvarDefs
 *      * value:
 *          * If type === 'any_object', then value is an object. The values within the object are anyvar.
 *          * If type === 'any_array', then value is an array of anyvar.
 *          * Else, value must be eosjs-compatible with the specified type (e.g. uint64 should be a string
 *            containing the value in decimal).
 *  * Other object. The values within the object are anyvar.
 *
 * The short form is more convenient, but it can't be converted back to binary (serialized).
 * Wherever the anyvar would have {type, value}, it has just the value instead.
 */
declare type Anyvar = null | string | number | Anyvar[] | {
    type: string;
    value: any;
} | Record<string, unknown>;
/** A type in an abi */
interface Type {
    /** Type name */
    name: string;
    /** Type name this is an alias of, if any */
    aliasOfName: string;
    /** Type this is an array of, if any */
    arrayOf?: Type;
    /** Type this is an optional of, if any */
    optionalOf?: Type;
    /** Marks binary extension fields */
    extensionOf?: Type;
    /** Base name of this type, if this is a struct */
    baseName: string;
    /** Base of this type, if this is a struct */
    base?: Type;
    /** Contained fields, if this is a struct */
    fields: Field[];
    /** Convert `data` to binary form and store in `buffer` */
    serialize: (buffer: SerialBuffer, data: any, state?: SerializerState, allowExtensions?: boolean) => void;
    /** Convert data in `buffer` from binary form */
    deserialize: (buffer: SerialBuffer, state?: SerializerState, allowExtensions?: boolean) => any;
}
/** Structural representation of a symbol */
interface Symbol {
    /** Name of the symbol, not including precision */
    name: string;
    /** Number of digits after the decimal point */
    precision: number;
}
interface Contract {
    actions: Map<string, Type>;
    types: Map<string, Type>;
}
interface Authorization {
    actor: string;
    permission: string;
}
/** Action with data in structured form */
interface Action {
    account: string;
    name: string;
    authorization: Authorization[];
    data: any;
    hex_data?: string;
}
/** Action with data in serialized hex form */
interface SerializedAction {
    account: string;
    name: string;
    authorization: Authorization[];
    data: string;
}
/** Serialize and deserialize data */
declare class SerialBuffer {
    /** Amount of valid data in `array` */
    length: number;
    /** Data in serialized (binary) form */
    array: Uint8Array;
    /** Current position while reading (deserializing) */
    readPos: number;
    textEncoder: TextEncoder;
    textDecoder: TextDecoder;
    /**
     * @param __namedParameters
     * `array`: `null` if serializing, or binary data to deserialize
     * `textEncoder`: `TextEncoder` instance to use. Pass in `null` if running in a browser
     * `textDecoder`: `TextDecider` instance to use. Pass in `null` if running in a browser
     */
    constructor({ array, textEncoder, textDecoder }?: {
        array?: Uint8Array | undefined;
        textEncoder?: TextEncoder | undefined;
        textDecoder?: TextDecoder | undefined;
    });
    /** Resize `array` if needed to have at least `size` bytes free */
    reserve(size: number): void;
    /** Is there data available to read? */
    haveReadData(): boolean;
    /** Restart reading from the beginning */
    restartRead(): void;
    /** Return data with excess storage trimmed away */
    asUint8Array(): Uint8Array;
    /** Append bytes */
    pushArray(v: number[] | Uint8Array): void;
    /** Append bytes */
    push(...v: number[]): void;
    /** Get a single byte */
    get(): number;
    /** Append bytes in `v`. Throws if `len` doesn't match `v.length` */
    pushUint8ArrayChecked(v: Uint8Array, len: number): void;
    /** Get `len` bytes */
    getUint8Array(len: number): Uint8Array;
    /** Skip `len` bytes */
    skip(len: number): void;
    /** Append a `uint16` */
    pushUint16(v: number): void;
    /** Get a `uint16` */
    getUint16(): number;
    /** Append a `uint32` */
    pushUint32(v: number): void;
    /** Get a `uint32` */
    getUint32(): number;
    /** Append a `uint64`. *Caution*: `number` only has 53 bits of precision */
    pushNumberAsUint64(v: number): void;
    /**
     * Get a `uint64` as a `number`. *Caution*: `number` only has 53 bits of precision; some values will change.
     * `numeric.binaryToDecimal(serialBuffer.getUint8Array(8))` recommended instead
     */
    getUint64AsNumber(): number;
    /** Append a `varuint32` */
    pushVaruint32(v: number): void;
    /** Get a `varuint32` */
    getVaruint32(): number;
    /** Append a `varint32` */
    pushVarint32(v: number): void;
    /** Get a `varint32` */
    getVarint32(): number;
    /** Append a `float32` */
    pushFloat32(v: number): void;
    /** Get a `float32` */
    getFloat32(): number;
    /** Append a `float64` */
    pushFloat64(v: number): void;
    /** Get a `float64` */
    getFloat64(): number;
    /** Append a `name` */
    pushName(s: string): void;
    /** Get a `name` */
    getName(): string;
    /** Append length-prefixed binary data */
    pushBytes(v: number[] | Uint8Array): void;
    /** Get length-prefixed binary data */
    getBytes(): Uint8Array;
    /** Append a string */
    pushString(v: string): void;
    /** Get a string */
    getString(): string;
    /** Append a `symbol_code`. Unlike `symbol`, `symbol_code` doesn't include a precision. */
    pushSymbolCode(name: string): void;
    /** Get a `symbol_code`. Unlike `symbol`, `symbol_code` doesn't include a precision. */
    getSymbolCode(): string;
    /** Append a `symbol` */
    pushSymbol({ name, precision, }: {
        name: string;
        precision: number;
    }): void;
    /** Get a `symbol` */
    getSymbol(): {
        name: string;
        precision: number;
    };
    /** Append an asset */
    pushAsset(s: string): void;
    /** Get an asset */
    getAsset(): string;
    /** Append a public key */
    pushPublicKey(s: string): void;
    /** Get a public key */
    getPublicKey(): string;
    /** Append a private key */
    pushPrivateKey(s: string): void;
    /** Get a private key */
    getPrivateKey(): string;
    /** Append a signature */
    pushSignature(s: string): void;
    /** Get a signature */
    getSignature(): string;
}
/** Is this a supported ABI version? */
declare const supportedAbiVersion: (version: string) => boolean;
/** Convert date in ISO format to `time_point` (miliseconds since epoch) */
declare const dateToTimePoint: (date: string) => number;
/** Convert `time_point` (miliseconds since epoch) to date in ISO format */
declare const timePointToDate: (us: number) => string;
/** Convert date in ISO format to `time_point_sec` (seconds since epoch) */
declare const dateToTimePointSec: (date: string) => number;
/** Convert `time_point_sec` (seconds since epoch) to to date in ISO format */
declare const timePointSecToDate: (sec: number) => string;
/** Convert date in ISO format to `block_timestamp_type` (half-seconds since a different epoch) */
declare const dateToBlockTimestamp: (date: string) => number;
/** Convert `block_timestamp_type` (half-seconds since a different epoch) to to date in ISO format */
declare const blockTimestampToDate: (slot: number) => string;
/** Convert `string` to `Symbol`. format: `precision,NAME`. */
declare const stringToSymbol: (s: string) => {
    name: string;
    precision: number;
};
/** Convert `Symbol` to `string`. format: `precision,NAME`. */
declare const symbolToString: ({ name, precision, }: {
    name: string;
    precision: number;
}) => string;
/** Convert binary data to hex */
declare const arrayToHex: (data: Uint8Array) => string;
/** Convert hex to binary data */
declare const hexToUint8Array: (hex: string) => Uint8Array;
/** Create the set of types built-in to the abi format */
declare const createInitialTypes: () => Map<string, Type>;
declare const createAbiTypes: () => Map<string, Type>;
declare const createTransactionExtensionTypes: () => Map<string, Type>;
declare const createTransactionTypes: () => Map<string, Type>;
/** Get type from `types` */
declare const getType: (types: Map<string, Type>, name: string) => Type;
/**
 * Get types from abi
 *
 * @param initialTypes Set of types to build on.
 * In most cases, it's best to fill this from a fresh call to `getTypesFromAbi()`.
 */
declare const getTypesFromAbi: (initialTypes: Map<string, Type>, abi?: Abi) => Map<string, Type>;
/** TAPoS: Return transaction fields which reference `refBlock` and expire `expireSeconds` after `timestamp` */
declare const transactionHeader: (refBlock: BlockTaposInfo, expireSeconds: number) => TransactionHeader;
/** Convert action data to serialized form (hex) */
declare const serializeActionData: (contract: Contract, account: string, name: string, data: any) => string;
/** Return action in serialized form */
declare const serializeAction: (contract: Contract, account: string, name: string, authorization: Authorization[], data: any) => SerializedAction;
/** Deserialize action data. If `data` is a `string`, then it's assumed to be in hex. */
declare const deserializeActionData: (contract: Contract, account: string, name: string, data: string | Uint8Array | number[]) => any;
/** Deserialize action. If `data` is a `string`, then it's assumed to be in hex. */
declare const deserializeAction: (contract: Contract, account: string, name: string, authorization: Authorization[], data: string | Uint8Array | number[]) => Action;
declare const serializeAnyvar: (buffer: SerialBuffer, anyvar: Anyvar) => void;
declare const deserializeAnyvar: (buffer: SerialBuffer, state?: SerializerState) => any;
declare const deserializeAnyvarShort: (buffer: SerialBuffer) => any;
declare const serializeAnyObject: (buffer: SerialBuffer, obj: any) => void;
declare const deserializeAnyObject: (buffer: SerialBuffer, state?: SerializerState) => any;
declare const serializeAnyArray: (buffer: SerialBuffer, arr: Anyvar[]) => void;
declare const deserializeAnyArray: (buffer: SerialBuffer, state?: SerializerState) => any[];
declare const serializeQuery: (buffer: SerialBuffer, query: Query) => void;
declare function b64tob64u(a: string): string;
declare function createBaseResolvedTransaction(): {
    expiration: string;
    ref_block_num: number;
    ref_block_prefix: number;
    max_net_usage_words: number;
    max_cpu_usage_ms: number;
    delay_sec: number;
    context_free_actions: never[];
    actions: never[];
    transaction_extensions: never[];
};

type Serialize_Field = Field;
type Serialize_SerializerOptions = SerializerOptions;
type Serialize_SerializerState = SerializerState;
declare const Serialize_SerializerState: typeof SerializerState;
type Serialize_Anyvar = Anyvar;
type Serialize_Type = Type;
type Serialize_Symbol = Symbol;
type Serialize_Contract = Contract;
type Serialize_Authorization = Authorization;
type Serialize_Action = Action;
type Serialize_SerializedAction = SerializedAction;
type Serialize_SerialBuffer = SerialBuffer;
declare const Serialize_SerialBuffer: typeof SerialBuffer;
declare const Serialize_supportedAbiVersion: typeof supportedAbiVersion;
declare const Serialize_dateToTimePoint: typeof dateToTimePoint;
declare const Serialize_timePointToDate: typeof timePointToDate;
declare const Serialize_dateToTimePointSec: typeof dateToTimePointSec;
declare const Serialize_timePointSecToDate: typeof timePointSecToDate;
declare const Serialize_dateToBlockTimestamp: typeof dateToBlockTimestamp;
declare const Serialize_blockTimestampToDate: typeof blockTimestampToDate;
declare const Serialize_stringToSymbol: typeof stringToSymbol;
declare const Serialize_symbolToString: typeof symbolToString;
declare const Serialize_arrayToHex: typeof arrayToHex;
declare const Serialize_hexToUint8Array: typeof hexToUint8Array;
declare const Serialize_createInitialTypes: typeof createInitialTypes;
declare const Serialize_createAbiTypes: typeof createAbiTypes;
declare const Serialize_createTransactionExtensionTypes: typeof createTransactionExtensionTypes;
declare const Serialize_createTransactionTypes: typeof createTransactionTypes;
declare const Serialize_getType: typeof getType;
declare const Serialize_getTypesFromAbi: typeof getTypesFromAbi;
declare const Serialize_transactionHeader: typeof transactionHeader;
declare const Serialize_serializeActionData: typeof serializeActionData;
declare const Serialize_serializeAction: typeof serializeAction;
declare const Serialize_deserializeActionData: typeof deserializeActionData;
declare const Serialize_deserializeAction: typeof deserializeAction;
declare const Serialize_serializeAnyvar: typeof serializeAnyvar;
declare const Serialize_deserializeAnyvar: typeof deserializeAnyvar;
declare const Serialize_deserializeAnyvarShort: typeof deserializeAnyvarShort;
declare const Serialize_serializeAnyObject: typeof serializeAnyObject;
declare const Serialize_deserializeAnyObject: typeof deserializeAnyObject;
declare const Serialize_serializeAnyArray: typeof serializeAnyArray;
declare const Serialize_deserializeAnyArray: typeof deserializeAnyArray;
declare const Serialize_serializeQuery: typeof serializeQuery;
declare const Serialize_b64tob64u: typeof b64tob64u;
declare const Serialize_createBaseResolvedTransaction: typeof createBaseResolvedTransaction;
declare namespace Serialize {
  export {
    Serialize_Field as Field,
    Serialize_SerializerOptions as SerializerOptions,
    Serialize_SerializerState as SerializerState,
    Serialize_Anyvar as Anyvar,
    Serialize_Type as Type,
    Serialize_Symbol as Symbol,
    Serialize_Contract as Contract,
    Serialize_Authorization as Authorization,
    Serialize_Action as Action,
    Serialize_SerializedAction as SerializedAction,
    Serialize_SerialBuffer as SerialBuffer,
    Serialize_supportedAbiVersion as supportedAbiVersion,
    Serialize_dateToTimePoint as dateToTimePoint,
    Serialize_timePointToDate as timePointToDate,
    Serialize_dateToTimePointSec as dateToTimePointSec,
    Serialize_timePointSecToDate as timePointSecToDate,
    Serialize_dateToBlockTimestamp as dateToBlockTimestamp,
    Serialize_blockTimestampToDate as blockTimestampToDate,
    Serialize_stringToSymbol as stringToSymbol,
    Serialize_symbolToString as symbolToString,
    Serialize_arrayToHex as arrayToHex,
    Serialize_hexToUint8Array as hexToUint8Array,
    Serialize_createInitialTypes as createInitialTypes,
    Serialize_createAbiTypes as createAbiTypes,
    Serialize_createTransactionExtensionTypes as createTransactionExtensionTypes,
    Serialize_createTransactionTypes as createTransactionTypes,
    Serialize_getType as getType,
    Serialize_getTypesFromAbi as getTypesFromAbi,
    Serialize_transactionHeader as transactionHeader,
    Serialize_serializeActionData as serializeActionData,
    Serialize_serializeAction as serializeAction,
    Serialize_deserializeActionData as deserializeActionData,
    Serialize_deserializeAction as deserializeAction,
    Serialize_serializeAnyvar as serializeAnyvar,
    Serialize_deserializeAnyvar as deserializeAnyvar,
    Serialize_deserializeAnyvarShort as deserializeAnyvarShort,
    Serialize_serializeAnyObject as serializeAnyObject,
    Serialize_deserializeAnyObject as deserializeAnyObject,
    Serialize_serializeAnyArray as serializeAnyArray,
    Serialize_deserializeAnyArray as deserializeAnyArray,
    Serialize_serializeQuery as serializeQuery,
    Serialize_b64tob64u as b64tob64u,
    Serialize_createBaseResolvedTransaction as createBaseResolvedTransaction,
  };
}

/**
 * @module RPC-API-Methods
 * copyright defined in eosjs/LICENSE.txt
 */

/** Structured format for abis */
interface Abi {
    version: string;
    types: {
        new_type_name: string;
        type: string;
    }[];
    structs: {
        name: string;
        base: string;
        fields: {
            name: string;
            type: string;
        }[];
    }[];
    actions: {
        name: string;
        type: string;
        ricardian_contract: string;
    }[];
    tables: {
        name: string;
        type: string;
        index_type: string;
        key_names: string[];
        key_types: string[];
    }[];
    ricardian_clauses: {
        id: string;
        body: string;
    }[];
    error_messages: {
        error_code: number;
        error_msg: string;
    }[];
    abi_extensions: {
        tag: number;
        value: string;
    }[];
    variants?: {
        name: string;
        types: string[];
    }[];
    action_results?: {
        name: string;
        result_type: string;
    }[];
    kv_tables?: {
        [key: string]: {
            type: string;
            primary_index: {
                name: string;
                type: string;
            };
            secondary_indices: {
                [key: string]: {
                    type: string;
                };
            }[];
        };
    }[];
}
interface BlockHeader {
    timestamp: string;
    producer: string;
    confirmed: number;
    previous: string;
    transaction_mroot: string;
    action_mroot: string;
    schedule_version: number;
    new_producers?: ProducerScheduleType;
    header_extensions: [number, string][];
}
interface SignedBlockHeader extends BlockHeader {
    producer_signature: string;
}
interface AccountResourceInfo {
    used: number;
    available: number;
    max: number;
    last_usage_update_time?: string;
    current_used?: number;
}
interface ResourceOverview {
    owner: string;
    ram_bytes: number;
    net_weight: string;
    cpu_weight: string;
}
interface ResourceDelegation {
    from: string;
    to: string;
    net_weight: string;
    cpu_weight: string;
}
interface RefundRequest {
    owner: string;
    request_time: string;
    net_amount: string;
    cpu_amount: string;
}
interface VoterInfo {
    owner: string;
    proxy: string;
    producers: string[];
    staked: number;
    last_vote_weight: string;
    proxied_vote_weight: string;
    is_proxy: number;
    flags1: number;
    reserved2: number;
    reserved3: string;
}
interface RexBalance {
    version: number;
    owner: string;
    vote_stake: string;
    rex_balance: string;
    matured_rex: number;
    rex_maturities: any;
}
interface Authority {
    threshold: number;
    keys: KeyWeight[];
    accounts: PermissionLevelWeight[];
    waits: WaitWeight[];
}
interface KeyWeight {
    key: string;
    weight: number;
}
interface Permission {
    perm_name: string;
    parent: string;
    required_auth: Authority;
}
interface PermissionLevel {
    actor: string;
    permission: string;
}
interface PermissionLevelWeight {
    permission: PermissionLevel;
    weight: number;
}
interface WaitWeight {
    wait_sec: number;
    weight: number;
}
/** Return value of `/v1/chain/abi_bin_to_json` */
interface AbiBinToJsonResult {
    args: "any";
}
/** Return value of `/v1/chain/abi_json_to_bin` */
interface AbiJsonToBinResult {
    binargs: "string";
}
/** Return value of `/v1/chain/get_abi` */
interface GetAbiResult {
    account_name: string;
    abi: Abi;
}
interface GetAccountResult {
    account_name: string;
    head_block_num: number | string;
    head_block_time: string;
    privileged: boolean;
    last_code_update: string;
    created: string;
    core_liquid_balance: string;
    ram_quota: number | string;
    net_weight: number | string;
    cpu_weight: number | string;
    net_limit: Limit;
    cpu_limit: Limit;
    ram_usage: number | string;
    permissions: PermissionElement[];
    total_resources: {
        owner: string;
        net_weight: string;
        cpu_weight: string;
        ram_bytes: number | string;
    };
    self_delegated_bandwidth: {
        from: string;
        to: string;
        net_weight: string;
        cpu_weight: string;
    };
    refund_request?: {
        cpu_amount: string;
        net_amount: string;
        request_time: string;
    };
    voter_info?: VoterInfo;
    rex_info?: RexInfo;
}
interface AccountResult {
    account_name: string;
    permission_name: string;
    authorizing_account?: Authorization;
    authorizing_key?: string;
    weight: number;
    threshold: number;
}
/** Return value of `/v1/chain/get_accounts_by_authorizers` */
interface GetAccountsByAuthorizersResult {
    accounts: AccountResult[];
}
interface GetActivatedProtocolFeaturesParams {
    limit?: number;
    search_by_block_num?: boolean;
    reverse?: boolean;
    lower_bound?: number;
    upper_bound?: number;
}
interface ActivatedProtocolFeature {
    feature_digest: string;
    activation_ordinal: number;
    activation_block_num: number;
    description_digest: string;
    dependencies: string[];
    protocol_feature_type: string;
    specification: {
        name: string;
        value: string;
    };
}
/** Return value of `/v1/chain/get_activated_protocol_features` */
interface GetActivatedProtocolFeaturesResult {
    activated_protocol_features: ActivatedProtocolFeature[];
    more?: number;
}
/** Return value of `/v1/chain/get_block_info` */
interface GetBlockInfoResult {
    timestamp: string;
    producer: string;
    confirmed: number;
    previous: string;
    transaction_mroot: string;
    action_mroot: string;
    schedule_version: number;
    producer_signature: string;
    id: string;
    block_num: number;
    ref_block_num: number;
    ref_block_prefix: number;
}
/** Returned action from nodeos, data is optional */
interface ProcessedAction {
    account: string;
    name: string;
    authorization: Authorization[];
    data?: any;
    hex_data?: string;
}
interface ProcessedTransaction {
    expiration?: string;
    ref_block_num?: number;
    ref_block_prefix?: number;
    max_net_usage_words?: number;
    max_cpu_usage_ms?: number;
    delay_sec?: number;
    context_free_actions?: ProcessedAction[];
    context_free_data?: Uint8Array[];
    actions: ProcessedAction[];
    transaction_extensions?: [number, string][];
}
interface PackedTransaction {
    id: string;
    signatures: string[];
    compression: number | string;
    packed_context_free_data: string;
    context_free_data: string[];
    packed_trx: string;
    transaction: ProcessedTransaction;
}
interface PackedTrx {
    signatures: string[];
    compression: number | string;
    packed_trx: string;
    packed_context_free_data: string;
}
interface TransactionReceipt extends TransactionReceiptHeader {
    trx: PackedTransaction;
}
/** Return value of `/v1/chain/get_block` */
interface GetBlockResult {
    timestamp: string;
    producer: string;
    confirmed: number;
    previous: string;
    transaction_mroot: string;
    action_mroot: string;
    schedule_version: number;
    new_producers: ProducerScheduleType | null;
    producer_signature: string;
    transactions: any;
    id: string;
    block_num: number;
    ref_block_prefix: number;
}
/** Used to calculate TAPoS fields in transactions */
interface BlockTaposInfo {
    block_num: number;
    id: string;
    timestamp?: string;
    header?: BlockHeader;
}
interface ProducerKey {
    producer_name: string;
    block_signing_key: string;
}
interface BlockSigningAuthority {
    threshold: number;
    keys: KeyWeight[];
}
interface ProducerAuthority {
    producer_name: string;
    authority: [number | string, BlockSigningAuthority];
}
interface ProducerAuthoritySchedule {
    version: number;
    producers: ProducerAuthority[];
}
interface ProducerScheduleType {
    version: number;
    producers: ProducerKey[];
}
interface ScheduleInfo {
    schedule_lib_num: number;
    schedule_hash: string;
    schedule: ProducerScheduleType;
}
interface IncrementalMerkle {
    _active_nodes: string[];
    _node_count: number;
}
interface ProtocolFeatureActivationSet {
    protocol_features: string[];
}
interface SecurityGroupInfo {
    version: number;
    participants: string[];
}
interface StateExtension {
    security_group_info: SecurityGroupInfo;
}
/** Return value of `/v1/chain/get_block_header_state` */
interface GetBlockHeaderStateResult {
    id: string;
    header: SignedBlockHeader;
    pending_schedule: ScheduleInfo;
    activated_protocol_features: ProtocolFeatureActivationSet;
    additional_signatures: string[];
    block_num: number;
    dpos_proposed_irreversible_blocknum: number;
    dpos_irreversible_blocknum: number;
    active_schedule: ProducerAuthoritySchedule;
    blockroot_merkle: IncrementalMerkle;
    producer_to_last_produced: Map<string, number>;
    producer_to_last_implied_irb: Map<string, number>;
    valid_block_signing_authority: any;
    confirm_count: number[];
    state_extension: [number, StateExtension];
}
/** Subset of `GetBlockHeaderStateResult` used to calculate TAPoS fields in transactions */
interface BlockHeaderStateTaposInfo {
    block_num: number;
    id: string;
    header: SignedBlockHeader;
}
/** Return value of `/v1/chain/get_code` */
interface GetCodeResult {
    account_name: string;
    code_hash: string;
    wast: string;
    wasm: string;
    abi: Abi;
}
/** Return value of `/v1/chain/get_code_hash` */
interface GetCodeHashResult {
    account_name: string;
    code_hash: string;
}
/** Return value of `/v1/chain/get_currency_stats` */
interface GetCurrencyStatsResult {
    [key: string]: {
        supply: string;
        max_supply: string;
        issuer: string;
    };
}
/** Return value of `/v1/chain/get_info` */
interface GetInfoResult {
    server_version: string;
    chain_id: string;
    head_block_num: number;
    last_irreversible_block_num: number;
    last_irreversible_block_id: string;
    last_irreversible_block_time?: string;
    head_block_id: string;
    head_block_time: string;
    head_block_producer: string;
    virtual_block_cpu_limit: number;
    virtual_block_net_limit: number;
    block_cpu_limit: number;
    block_net_limit: number;
    server_version_string?: string;
    fork_db_head_block_num?: number;
    fork_db_head_block_id?: string;
    server_full_version_string?: string;
    first_block_num?: number;
}
/** Return value of /v1/chain/get_producer_schedule */
interface GetProducerScheduleResult {
    active: ProducerAuthoritySchedule | null;
    pending: ProducerAuthoritySchedule | null;
    proposed: ProducerAuthoritySchedule | null;
}
interface ProducerDetails {
    owner: string;
    producer_authority?: any[];
    url: string;
    is_active?: number;
    total_votes: string;
    producer_key: string;
    unpaid_blocks?: number;
    last_claim_time?: string;
    location?: number;
}
/** Return value of `/v1/chain/get_producers` */
interface GetProducersResult {
    rows: ProducerDetails[];
    total_producer_vote_weight: string;
    more: string;
}
/** Return value of `/v1/chain/get_raw_code_and_abi` */
interface GetRawCodeAndAbiResult {
    account_name: string;
    wasm: string;
    abi: string;
}
/** Return value of `/v1/chain/get_raw_abi` */
interface GetRawAbiResult {
    account_name: string;
    code_hash: string;
    abi_hash: string;
    abi: string;
}
interface DeferredTransaction extends ProcessedTransaction {
    deferred_transaction_generation?: {
        sender_trx_id: string;
        sender_id: string;
        sender: string;
    };
}
interface GeneratedTransaction {
    trx_id: string;
    sender: string;
    sender_id: string;
    payer: string;
    delay_until: string;
    expiration: string;
    published: string;
    packed_trx?: string[];
    transaction?: DeferredTransaction[];
}
/** Return value of `/v1/chain/get_scheduled_transactions` */
interface GetScheduledTransactionsResult {
    transactions: GeneratedTransaction[];
    more: string;
}
/** Return value of `/v1/chain/get_table_rows` and `/v1/chain/get_kv_table_rows` */
interface GetTableRowsResult {
    rows: any[];
    more: boolean;
    next_key: string;
    next_key_bytes: string;
}
interface GetTableByScopeResultRow {
    code: string;
    scope: string;
    table: string;
    payer: string;
    count: number;
}
/** Return value of `/v1/chain/get_table_by_scope` */
interface GetTableByScopeResult {
    rows: GetTableByScopeResultRow[];
    more: string;
}
/** Arguments for `push_transaction` */
interface PushTransactionArgs {
    signatures: string[];
    compression?: number;
    serializedTransaction: Uint8Array;
    serializedContextFreeData?: Uint8Array;
    transactionHeader?: TransactionHeader;
}
/** Return value of `/v1/chain/push_ro_transaction` */
interface ReadOnlyTransactResult {
    head_block_num: number;
    head_block_id: string;
    last_irreversible_block_num: number;
    last_irreversible_block_id: string;
    code_hash: string;
    pending_transactions: string[];
    result: TransactionTrace;
}
interface DBSizeIndexCount {
    index: string;
    row_count: number;
}
/** Return value of `/v1/db_size/get` */
interface DBSizeGetResult {
    free_bytes: number;
    used_bytes: number;
    size: number;
    indices: DBSizeIndexCount[];
}
interface TraceApiAction {
    global_sequence: number;
    receiver: string;
    account: string;
    action: string;
    authorization: Authorization[];
    data: any;
    return_value: any;
}
interface TraceApiTransactionHeader {
    expiration: string;
    ref_block_num: number;
    ref_block_prefix: number;
    max_net_usage_words: number;
    max_cpu_usage_ms: number;
    delay_sec: number;
}
interface TraceApiTransaction {
    id: string;
    actions: TraceApiAction[];
    status?: string;
    cpu_usage_us?: number;
    net_usage_words?: number;
    signatures?: string[];
    transaction_header?: TraceApiTransactionHeader;
    bill_to_accounts: string[];
}
/** Return value of `/v1/trace_api/get_block` */
interface TraceApiGetBlockResult {
    id: string;
    number: number;
    previous_id: string;
    status: string;
    timestamp: string;
    producer: string;
    transaction_mroot?: string;
    action_mroot?: string;
    schedule_version: number;
    transactions: TraceApiTransaction;
}
interface OrderedActionResult {
    global_action_seq: number;
    account_action_seq: number;
    block_num: number;
    block_time: string;
    action_trace: any;
}
/** Return value of `/v1/history/get_actions` */
interface GetActionsResult {
    actions: OrderedActionResult[];
    last_irreversible_block: number;
    time_limit_exceeded_error?: boolean;
}
/** Return value of `/v1/history/get_transaction` */
interface GetTransactionResult {
    id: string;
    trx: any;
    block_time: string;
    block_num: number;
    last_irreversible_block: number;
    traces: any[];
}
/** Return value of `/v1/history/get_key_accounts` */
interface GetKeyAccountsResult {
    account_names: string[];
}
/** Return value of `/v1/history/get_controlled_accounts` */
interface GetControlledAccountsResult {
    controlled_accounts: string[];
}
interface RexInfo {
    matured_rex: number;
    owner: string;
    rex_balance: string;
    rex_maturities: any[];
    version: number;
    vote_stake: string;
}
interface Limit {
    used: number | string;
    available: number | string;
    max: number | string;
    last_usage_update_time: string;
    current_used: number | string;
}
interface PermissionElement {
    perm_name: string;
    parent: string;
    required_auth: RequiredAuth;
}
interface RequiredAuth {
    threshold: number;
    keys: {
        key: string;
        weight: number;
    }[];
    accounts: {
        permission: {
            actor: string;
            permission: string;
        };
        weight: number;
    }[];
    waits: {
        wait_sec: number;
        weight: number;
    }[];
}
/** PROTON */
declare type KycInfo = {
    kyc_provider: string;
    kyc_level: string;
    kyc_date: number;
};
declare type KycProvider = {
    blisted: number;
    desc: string;
    iconurl: string;
    kyc_provider: string;
    name: string;
    url: string;
};
declare type UserInfo = {
    acc: string;
    avatar: string;
    date: number;
    aacts: any[];
    ac: any[];
    isLightKYCVerified?: boolean;
    isTier1KYCVerified?: boolean;
    isTier2KYCVerified?: boolean;
    isTier3KYCVerified?: boolean;
    kyc: KycInfo[];
    name: string;
    raccs: any[];
    verified: number;
    verifiedon: number;
    verifier: string;
};
interface RsaKey {
    modulus: string;
    exponent: string;
}
interface WaKey {
    index?: number;
    account?: string;
    key_name?: string;
    key: {
        key: [string, string | RsaKey];
        user_presence: number;
        rpid: string;
    };
    nonce?: number;
    fullKey: string;
    isAccountPerm?: boolean;
    isEcc?: boolean;
    isRsa?: boolean;
    isEth?: boolean;
    credential_id?: string;
}
/**
 * GET TRANSACTION
 */
interface NativeTransaction {
    block_num: number;
    block_time: string;
    head_block_num: number;
    id: string;
    irreversible: boolean;
    last_irreversible_block: number;
    traces: ActionTrace[];
    transaction_num: number;
    trx: {
        receipt: TransactionReceiptHeader & {
            trx: [
                number,
                {
                    compression: number | string;
                    packed_context_free_data: string;
                    packed_trx: string;
                    signatures: string[];
                }
            ];
        };
        trx: ProcessedTransaction;
    };
}

type RpcInterfaces_Abi = Abi;
type RpcInterfaces_BlockHeader = BlockHeader;
type RpcInterfaces_SignedBlockHeader = SignedBlockHeader;
type RpcInterfaces_AccountResourceInfo = AccountResourceInfo;
type RpcInterfaces_ResourceOverview = ResourceOverview;
type RpcInterfaces_ResourceDelegation = ResourceDelegation;
type RpcInterfaces_RefundRequest = RefundRequest;
type RpcInterfaces_VoterInfo = VoterInfo;
type RpcInterfaces_RexBalance = RexBalance;
type RpcInterfaces_Authority = Authority;
type RpcInterfaces_KeyWeight = KeyWeight;
type RpcInterfaces_Permission = Permission;
type RpcInterfaces_PermissionLevel = PermissionLevel;
type RpcInterfaces_PermissionLevelWeight = PermissionLevelWeight;
type RpcInterfaces_WaitWeight = WaitWeight;
type RpcInterfaces_AbiBinToJsonResult = AbiBinToJsonResult;
type RpcInterfaces_AbiJsonToBinResult = AbiJsonToBinResult;
type RpcInterfaces_GetAbiResult = GetAbiResult;
type RpcInterfaces_GetAccountResult = GetAccountResult;
type RpcInterfaces_AccountResult = AccountResult;
type RpcInterfaces_GetAccountsByAuthorizersResult = GetAccountsByAuthorizersResult;
type RpcInterfaces_GetActivatedProtocolFeaturesParams = GetActivatedProtocolFeaturesParams;
type RpcInterfaces_ActivatedProtocolFeature = ActivatedProtocolFeature;
type RpcInterfaces_GetActivatedProtocolFeaturesResult = GetActivatedProtocolFeaturesResult;
type RpcInterfaces_GetBlockInfoResult = GetBlockInfoResult;
type RpcInterfaces_ProcessedAction = ProcessedAction;
type RpcInterfaces_ProcessedTransaction = ProcessedTransaction;
type RpcInterfaces_PackedTransaction = PackedTransaction;
type RpcInterfaces_PackedTrx = PackedTrx;
type RpcInterfaces_TransactionReceipt = TransactionReceipt;
type RpcInterfaces_GetBlockResult = GetBlockResult;
type RpcInterfaces_BlockTaposInfo = BlockTaposInfo;
type RpcInterfaces_ProducerKey = ProducerKey;
type RpcInterfaces_BlockSigningAuthority = BlockSigningAuthority;
type RpcInterfaces_ProducerAuthority = ProducerAuthority;
type RpcInterfaces_ProducerAuthoritySchedule = ProducerAuthoritySchedule;
type RpcInterfaces_ProducerScheduleType = ProducerScheduleType;
type RpcInterfaces_ScheduleInfo = ScheduleInfo;
type RpcInterfaces_IncrementalMerkle = IncrementalMerkle;
type RpcInterfaces_ProtocolFeatureActivationSet = ProtocolFeatureActivationSet;
type RpcInterfaces_SecurityGroupInfo = SecurityGroupInfo;
type RpcInterfaces_StateExtension = StateExtension;
type RpcInterfaces_GetBlockHeaderStateResult = GetBlockHeaderStateResult;
type RpcInterfaces_BlockHeaderStateTaposInfo = BlockHeaderStateTaposInfo;
type RpcInterfaces_GetCodeResult = GetCodeResult;
type RpcInterfaces_GetCodeHashResult = GetCodeHashResult;
type RpcInterfaces_GetCurrencyStatsResult = GetCurrencyStatsResult;
type RpcInterfaces_GetInfoResult = GetInfoResult;
type RpcInterfaces_GetProducerScheduleResult = GetProducerScheduleResult;
type RpcInterfaces_ProducerDetails = ProducerDetails;
type RpcInterfaces_GetProducersResult = GetProducersResult;
type RpcInterfaces_GetRawCodeAndAbiResult = GetRawCodeAndAbiResult;
type RpcInterfaces_GetRawAbiResult = GetRawAbiResult;
type RpcInterfaces_DeferredTransaction = DeferredTransaction;
type RpcInterfaces_GeneratedTransaction = GeneratedTransaction;
type RpcInterfaces_GetScheduledTransactionsResult = GetScheduledTransactionsResult;
type RpcInterfaces_GetTableRowsResult = GetTableRowsResult;
type RpcInterfaces_GetTableByScopeResultRow = GetTableByScopeResultRow;
type RpcInterfaces_GetTableByScopeResult = GetTableByScopeResult;
type RpcInterfaces_PushTransactionArgs = PushTransactionArgs;
type RpcInterfaces_ReadOnlyTransactResult = ReadOnlyTransactResult;
type RpcInterfaces_DBSizeIndexCount = DBSizeIndexCount;
type RpcInterfaces_DBSizeGetResult = DBSizeGetResult;
type RpcInterfaces_TraceApiAction = TraceApiAction;
type RpcInterfaces_TraceApiTransactionHeader = TraceApiTransactionHeader;
type RpcInterfaces_TraceApiTransaction = TraceApiTransaction;
type RpcInterfaces_TraceApiGetBlockResult = TraceApiGetBlockResult;
type RpcInterfaces_OrderedActionResult = OrderedActionResult;
type RpcInterfaces_GetActionsResult = GetActionsResult;
type RpcInterfaces_GetTransactionResult = GetTransactionResult;
type RpcInterfaces_GetKeyAccountsResult = GetKeyAccountsResult;
type RpcInterfaces_GetControlledAccountsResult = GetControlledAccountsResult;
type RpcInterfaces_RexInfo = RexInfo;
type RpcInterfaces_Limit = Limit;
type RpcInterfaces_PermissionElement = PermissionElement;
type RpcInterfaces_RequiredAuth = RequiredAuth;
type RpcInterfaces_KycInfo = KycInfo;
type RpcInterfaces_KycProvider = KycProvider;
type RpcInterfaces_UserInfo = UserInfo;
type RpcInterfaces_RsaKey = RsaKey;
type RpcInterfaces_WaKey = WaKey;
type RpcInterfaces_NativeTransaction = NativeTransaction;
declare namespace RpcInterfaces {
  export {
    RpcInterfaces_Abi as Abi,
    RpcInterfaces_BlockHeader as BlockHeader,
    RpcInterfaces_SignedBlockHeader as SignedBlockHeader,
    RpcInterfaces_AccountResourceInfo as AccountResourceInfo,
    RpcInterfaces_ResourceOverview as ResourceOverview,
    RpcInterfaces_ResourceDelegation as ResourceDelegation,
    RpcInterfaces_RefundRequest as RefundRequest,
    RpcInterfaces_VoterInfo as VoterInfo,
    RpcInterfaces_RexBalance as RexBalance,
    RpcInterfaces_Authority as Authority,
    RpcInterfaces_KeyWeight as KeyWeight,
    RpcInterfaces_Permission as Permission,
    RpcInterfaces_PermissionLevel as PermissionLevel,
    RpcInterfaces_PermissionLevelWeight as PermissionLevelWeight,
    RpcInterfaces_WaitWeight as WaitWeight,
    RpcInterfaces_AbiBinToJsonResult as AbiBinToJsonResult,
    RpcInterfaces_AbiJsonToBinResult as AbiJsonToBinResult,
    RpcInterfaces_GetAbiResult as GetAbiResult,
    RpcInterfaces_GetAccountResult as GetAccountResult,
    RpcInterfaces_AccountResult as AccountResult,
    RpcInterfaces_GetAccountsByAuthorizersResult as GetAccountsByAuthorizersResult,
    RpcInterfaces_GetActivatedProtocolFeaturesParams as GetActivatedProtocolFeaturesParams,
    RpcInterfaces_ActivatedProtocolFeature as ActivatedProtocolFeature,
    RpcInterfaces_GetActivatedProtocolFeaturesResult as GetActivatedProtocolFeaturesResult,
    RpcInterfaces_GetBlockInfoResult as GetBlockInfoResult,
    RpcInterfaces_ProcessedAction as ProcessedAction,
    RpcInterfaces_ProcessedTransaction as ProcessedTransaction,
    RpcInterfaces_PackedTransaction as PackedTransaction,
    RpcInterfaces_PackedTrx as PackedTrx,
    RpcInterfaces_TransactionReceipt as TransactionReceipt,
    RpcInterfaces_GetBlockResult as GetBlockResult,
    RpcInterfaces_BlockTaposInfo as BlockTaposInfo,
    RpcInterfaces_ProducerKey as ProducerKey,
    RpcInterfaces_BlockSigningAuthority as BlockSigningAuthority,
    RpcInterfaces_ProducerAuthority as ProducerAuthority,
    RpcInterfaces_ProducerAuthoritySchedule as ProducerAuthoritySchedule,
    RpcInterfaces_ProducerScheduleType as ProducerScheduleType,
    RpcInterfaces_ScheduleInfo as ScheduleInfo,
    RpcInterfaces_IncrementalMerkle as IncrementalMerkle,
    RpcInterfaces_ProtocolFeatureActivationSet as ProtocolFeatureActivationSet,
    RpcInterfaces_SecurityGroupInfo as SecurityGroupInfo,
    RpcInterfaces_StateExtension as StateExtension,
    RpcInterfaces_GetBlockHeaderStateResult as GetBlockHeaderStateResult,
    RpcInterfaces_BlockHeaderStateTaposInfo as BlockHeaderStateTaposInfo,
    RpcInterfaces_GetCodeResult as GetCodeResult,
    RpcInterfaces_GetCodeHashResult as GetCodeHashResult,
    RpcInterfaces_GetCurrencyStatsResult as GetCurrencyStatsResult,
    RpcInterfaces_GetInfoResult as GetInfoResult,
    RpcInterfaces_GetProducerScheduleResult as GetProducerScheduleResult,
    RpcInterfaces_ProducerDetails as ProducerDetails,
    RpcInterfaces_GetProducersResult as GetProducersResult,
    RpcInterfaces_GetRawCodeAndAbiResult as GetRawCodeAndAbiResult,
    RpcInterfaces_GetRawAbiResult as GetRawAbiResult,
    RpcInterfaces_DeferredTransaction as DeferredTransaction,
    RpcInterfaces_GeneratedTransaction as GeneratedTransaction,
    RpcInterfaces_GetScheduledTransactionsResult as GetScheduledTransactionsResult,
    RpcInterfaces_GetTableRowsResult as GetTableRowsResult,
    RpcInterfaces_GetTableByScopeResultRow as GetTableByScopeResultRow,
    RpcInterfaces_GetTableByScopeResult as GetTableByScopeResult,
    RpcInterfaces_PushTransactionArgs as PushTransactionArgs,
    RpcInterfaces_ReadOnlyTransactResult as ReadOnlyTransactResult,
    RpcInterfaces_DBSizeIndexCount as DBSizeIndexCount,
    RpcInterfaces_DBSizeGetResult as DBSizeGetResult,
    RpcInterfaces_TraceApiAction as TraceApiAction,
    RpcInterfaces_TraceApiTransactionHeader as TraceApiTransactionHeader,
    RpcInterfaces_TraceApiTransaction as TraceApiTransaction,
    RpcInterfaces_TraceApiGetBlockResult as TraceApiGetBlockResult,
    RpcInterfaces_OrderedActionResult as OrderedActionResult,
    RpcInterfaces_GetActionsResult as GetActionsResult,
    RpcInterfaces_GetTransactionResult as GetTransactionResult,
    RpcInterfaces_GetKeyAccountsResult as GetKeyAccountsResult,
    RpcInterfaces_GetControlledAccountsResult as GetControlledAccountsResult,
    RpcInterfaces_RexInfo as RexInfo,
    RpcInterfaces_Limit as Limit,
    RpcInterfaces_PermissionElement as PermissionElement,
    RpcInterfaces_RequiredAuth as RequiredAuth,
    RpcInterfaces_KycInfo as KycInfo,
    RpcInterfaces_KycProvider as KycProvider,
    RpcInterfaces_UserInfo as UserInfo,
    RpcInterfaces_RsaKey as RsaKey,
    RpcInterfaces_WaKey as WaKey,
    RpcInterfaces_NativeTransaction as NativeTransaction,
  };
}

/**
 * @module Javascript-API
 */

/** Arguments to `getRequiredKeys` */
interface AuthorityProviderArgs {
    /** Transaction that needs to be signed */
    transaction: any;
    /** Public keys associated with the private keys that the `SignatureProvider` holds */
    availableKeys: string[];
}
/** Get subset of `availableKeys` needed to meet authorities in `transaction` */
interface AuthorityProvider {
    /** Get subset of `availableKeys` needed to meet authorities in `transaction` */
    getRequiredKeys: (args: AuthorityProviderArgs) => Promise<string[]>;
}
/** Retrieves raw ABIs for a specified accountName */
interface AbiProvider {
    /** Retrieve the BinaryAbi */
    getRawAbi: (accountName: string) => Promise<BinaryAbi>;
}
/** Structure for the raw form of ABIs */
interface BinaryAbi {
    /** account which has deployed the ABI */
    accountName: string;
    /** abi in binary form */
    abi: Uint8Array;
}
/** Holds a fetched abi */
interface CachedAbi {
    /** abi in binary form */
    rawAbi: Uint8Array;
    /** abi in structured form */
    abi: Abi;
}
/** Arguments to `sign` */
interface SignatureProviderArgs {
    /** Chain transaction is for */
    chainId: string;
    /** Public keys associated with the private keys needed to sign the transaction */
    requiredKeys: string[];
    /** Transaction to sign */
    serializedTransaction: Uint8Array;
    /** Context-free data to sign */
    serializedContextFreeData?: Uint8Array;
    /** ABIs for all contracts with actions included in `serializedTransaction` */
    abis?: BinaryAbi[];
}
/** Signs transactions */
interface SignatureProvider {
    /** Public keys associated with the private keys that the `SignatureProvider` holds */
    getAvailableKeys: () => Promise<string[]>;
    /** Sign a transaction */
    sign: (args: SignatureProviderArgs) => Promise<PushTransactionArgs>;
}
interface ResourcePayer {
    payer: string;
    max_net_bytes: number;
    max_cpu_us: number;
    max_memory_bytes: number;
}
interface Transaction {
    expiration?: string;
    ref_block_num?: number;
    ref_block_prefix?: number;
    max_net_usage_words?: number;
    max_cpu_usage_ms?: number;
    delay_sec?: number;
    context_free_actions?: Action[];
    context_free_data?: Uint8Array[];
    actions: Action[];
    transaction_extensions?: [number, string][];
    resource_payer?: ResourcePayer;
}
interface TransactionHeader {
    expiration: string;
    ref_block_num: number;
    ref_block_prefix: number;
}
interface AccountDelta {
    account: string;
    delta: number;
}
interface AuthSequence {
    account: string;
    sequence: number;
}
interface ActionReceipt {
    receiver: string;
    act_digest: string;
    global_sequence: number;
    recv_sequence: number;
    auth_sequence: [string, number][];
    code_sequence: number;
    abi_sequence: number;
}
interface ActionTrace {
    action_ordinal: number;
    creator_action_ordinal: number;
    closest_unnotified_ancestor_action_ordinal: number;
    receipt: ActionReceipt;
    receiver: string;
    act: ProcessedAction;
    context_free: boolean;
    elapsed: number;
    console: string;
    trx_id: string;
    block_num: number;
    block_time: string;
    producer_block_id: string | null;
    account_ram_deltas: AccountDelta[];
    account_disk_deltas: AccountDelta[];
    except: any;
    error_code: number | null;
    return_value?: any;
    return_value_hex_data?: string;
    return_value_data?: any;
    inline_traces?: ActionTrace[];
}
interface TransactionReceiptHeader {
    status: string;
    cpu_usage_us: number;
    net_usage_words: number;
}
interface TransactionTrace {
    id: string;
    block_num: number;
    block_time: string;
    producer_block_id: string | null;
    receipt: TransactionReceiptHeader | null;
    elapsed: number;
    net_usage: number;
    scheduled: boolean;
    action_traces: ActionTrace[];
    account_ram_delta: AccountDelta | null;
    except: string | null;
    error_code: number | null;
    bill_to_accounts: string[];
}
interface TransactResult {
    transaction_id?: string;
    processed: TransactionTrace;
}
/** Optional query configuration object */
interface QueryConfig {
    sign?: boolean;
    requiredKeys?: string[];
    authorization?: Authorization[];
}
/**
 * A Query may be any of the following:
 * * string:                                           method
 * * [string, Query[]]:                                [method, filter]
 * * [string, Anyvar, Query[]]:                        [method, arg, filter]
 * * {method: string, arg?: Anyvar, filter?: Query[]}  explicit form
 */
declare type Query = string | [string, Query[]] | [string, Anyvar, Query[]] | {
    method: string;
    arg?: Anyvar;
    filter?: Query[];
};
declare type ContextFreeGroupCallback = (index: {
    cfa: number;
    cfd: number;
}) => {
    action?: SerializedAction;
    contextFreeAction?: SerializedAction;
    contextFreeData?: Uint8Array;
};
interface ActionSerializerType {
    [actionName: string]: any;
}
/** Optional transact configuration object */
interface TransactConfig {
    broadcast?: boolean;
    sign?: boolean;
    readOnlyTrx?: boolean;
    returnFailureTraces?: boolean;
    requiredKeys?: string[];
    compression?: boolean;
    blocksBehind?: number;
    useLastIrreversible?: boolean;
    expireSeconds?: number;
}
/** NEW: Optional transact configuration object */
interface TransactConfig {
    broadcast?: boolean;
    sign?: boolean;
    compression?: boolean;
    blocksBehind?: number;
    useLastIrreversible?: boolean;
    expireSeconds?: number;
    requiredKeys?: string[];
    transactionHeader?: any;
}
interface MessageTypeProperty {
    name: string;
    type: string;
}
interface MessageTypes {
    EIP712Domain: MessageTypeProperty[];
    [additionalProperties: string]: MessageTypeProperty[];
}
declare type SignedMsgParams<D> = Required<MsgParams<D>>;
interface MsgParams<D> {
    data: D;
    sig?: string;
}
interface EIP712TypedData {
    name: string;
    type: string;
    value: any;
}
declare type TypedData = string | EIP712TypedData | EIP712TypedData[];
declare type RecoverPersonalSignature = <T extends MessageTypes>(msgParams: SignedMsgParams<TypedData | TypedMessage<T>>) => string;
interface TypedMessage<T extends MessageTypes> {
    types: T;
    primaryType: keyof T;
    domain: {
        name?: string;
        version?: string;
        chainId?: number;
        verifyingContract?: string;
    };
    message: Record<string, unknown>;
}
declare type WaExecAction = {
    account: string;
    name: string;
    authorization: Authorization[];
    data: {
        account: string;
        key: {
            key: [string, any];
            user_presence: number;
            rpid: string;
        };
        signature: {
            auth_data: string;
            signature: string;
            client_json: string;
        };
        nonce: number;
        trx: Transaction;
    };
    hex_data?: string;
};
interface ClientDataJSON {
    type: "webauthn.get" | "webauthn.create";
    challenge: string;
    origin: string;
    tokenBindingId?: string;
}

type ApiInterfaces_AuthorityProviderArgs = AuthorityProviderArgs;
type ApiInterfaces_AuthorityProvider = AuthorityProvider;
type ApiInterfaces_AbiProvider = AbiProvider;
type ApiInterfaces_BinaryAbi = BinaryAbi;
type ApiInterfaces_CachedAbi = CachedAbi;
type ApiInterfaces_SignatureProviderArgs = SignatureProviderArgs;
type ApiInterfaces_SignatureProvider = SignatureProvider;
type ApiInterfaces_ResourcePayer = ResourcePayer;
type ApiInterfaces_Transaction = Transaction;
type ApiInterfaces_TransactConfig = TransactConfig;
type ApiInterfaces_TransactionHeader = TransactionHeader;
type ApiInterfaces_AccountDelta = AccountDelta;
type ApiInterfaces_AuthSequence = AuthSequence;
type ApiInterfaces_ActionReceipt = ActionReceipt;
type ApiInterfaces_ActionTrace = ActionTrace;
type ApiInterfaces_TransactionReceiptHeader = TransactionReceiptHeader;
type ApiInterfaces_TransactionTrace = TransactionTrace;
type ApiInterfaces_TransactResult = TransactResult;
type ApiInterfaces_QueryConfig = QueryConfig;
type ApiInterfaces_Query = Query;
type ApiInterfaces_ContextFreeGroupCallback = ContextFreeGroupCallback;
type ApiInterfaces_ActionSerializerType = ActionSerializerType;
type ApiInterfaces_SignedMsgParams<D> = SignedMsgParams<D>;
type ApiInterfaces_MsgParams<D> = MsgParams<D>;
type ApiInterfaces_TypedData = TypedData;
type ApiInterfaces_RecoverPersonalSignature = RecoverPersonalSignature;
type ApiInterfaces_TypedMessage<T extends MessageTypes> = TypedMessage<T>;
type ApiInterfaces_WaExecAction = WaExecAction;
type ApiInterfaces_ClientDataJSON = ClientDataJSON;
declare namespace ApiInterfaces {
  export {
    ApiInterfaces_AuthorityProviderArgs as AuthorityProviderArgs,
    ApiInterfaces_AuthorityProvider as AuthorityProvider,
    ApiInterfaces_AbiProvider as AbiProvider,
    ApiInterfaces_BinaryAbi as BinaryAbi,
    ApiInterfaces_CachedAbi as CachedAbi,
    ApiInterfaces_SignatureProviderArgs as SignatureProviderArgs,
    ApiInterfaces_SignatureProvider as SignatureProvider,
    ApiInterfaces_ResourcePayer as ResourcePayer,
    ApiInterfaces_Transaction as Transaction,
    ApiInterfaces_TransactConfig as TransactConfig,
    ApiInterfaces_TransactionHeader as TransactionHeader,
    ApiInterfaces_AccountDelta as AccountDelta,
    ApiInterfaces_AuthSequence as AuthSequence,
    ApiInterfaces_ActionReceipt as ActionReceipt,
    ApiInterfaces_ActionTrace as ActionTrace,
    ApiInterfaces_TransactionReceiptHeader as TransactionReceiptHeader,
    ApiInterfaces_TransactionTrace as TransactionTrace,
    ApiInterfaces_TransactResult as TransactResult,
    ApiInterfaces_QueryConfig as QueryConfig,
    ApiInterfaces_Query as Query,
    ApiInterfaces_ContextFreeGroupCallback as ContextFreeGroupCallback,
    ApiInterfaces_ActionSerializerType as ActionSerializerType,
    ApiInterfaces_SignedMsgParams as SignedMsgParams,
    ApiInterfaces_MsgParams as MsgParams,
    ApiInterfaces_TypedData as TypedData,
    ApiInterfaces_RecoverPersonalSignature as RecoverPersonalSignature,
    ApiInterfaces_TypedMessage as TypedMessage,
    ApiInterfaces_WaExecAction as WaExecAction,
    ApiInterfaces_ClientDataJSON as ClientDataJSON,
  };
}

/**
 * Checks blockchain for a list of kycproviders, and sorts through the ones that are blacklisted.
 * @returns An array of strings with valid kyc provider names.
 */
declare function getValidKycProviders(this: JsonRpc): Promise<void>;
/**
 * Takes an account or a list of accounts and checks to make sure that they are light-verified
 * @param account This could be an array of user rows from the usersinfo table on the blockchain, or a singular string for an account name
 * @returns An object of the user data as pulled from the usersinfo table on the blockchain with an additional key, isLightKYCVerified (boolean)
 */
declare function isLightKYCVerified(this: JsonRpc, account: UserInfo[] | string): Promise<UserInfo[]>;
declare function fetchCredentials(this: JsonRpc, actor: string): Promise<WaKey[]>;

/**
 * @module RPC-Error
 */
/** Holds detailed error information */
declare class RpcError extends Error {
    /** Detailed error information */
    json: any;
    details: any;
    constructor(json: any);
}

/** Make RPC calls */
declare class JsonRpc implements AuthorityProvider, AbiProvider {
    initialEndpoints: string[];
    endpoints: string[];
    currentEndpoint: string;
    validKycProviders: string[];
    timeout: number;
    /**
     * @param args
     *`fetch`:
     * browsers: leave `null` or `undefined`
     * node: provide an implementation
     */
    constructor(endpoints?: string | string[], options?: {
        timeout?: number;
    });
    nextEndpoint(): void;
    /** Post `body` to `endpoint + path`. Throws detailed error information in `RpcError` when available. */
    fetch<R = any>(path: string, body: any, currentRetries?: number, logError?: boolean): Promise<R>;
    /** Get from endpoint  */
    get(path: string): Promise<any>;
    abi_bin_to_json(code: string, action: string, binargs: string): Promise<AbiBinToJsonResult>;
    abi_json_to_bin(code: string, action: string, args: any[]): Promise<AbiJsonToBinResult>;
    /** Raw call to `/v1/chain/get_abi` */
    get_abi(accountName: string): Promise<GetAbiResult>;
    /** Raw call to `/v1/chain/get_account` */
    get_account(accountName: string): Promise<GetAccountResult>;
    /** Raw call to `/v1/chain/get_accounts_by_authorizers` */
    get_accounts_by_authorizers(accounts: Authorization[], keys: string[]): Promise<GetAccountsByAuthorizersResult>;
    /** Raw call to `get_activated_protocol_features` */
    get_activated_protocol_features({ limit, search_by_block_num, reverse, lower_bound, upper_bound, }?: GetActivatedProtocolFeaturesParams): Promise<GetActivatedProtocolFeaturesResult>;
    /** Raw call to `/v1/chain/get_block_header_state` */
    get_block_header_state(blockNumOrId: number | string): Promise<GetBlockHeaderStateResult>;
    /** Raw call to `/v1/chain/get_block_info` */
    get_block_info(blockNum: number): Promise<GetBlockInfoResult>;
    /** Raw call to `/v1/chain/get_block` */
    get_block(blockNumOrId: number | string): Promise<GetBlockResult>;
    /** Raw call to `/v1/chain/get_code` */
    get_code(accountName: string): Promise<GetCodeResult>;
    /** Raw call to `/v1/chain/get_code_hash` */
    get_code_hash(accountName: string): Promise<GetCodeHashResult>;
    /** Raw call to `/v1/chain/get_currency_balance` */
    get_currency_balance(code: string, account: string, symbol: string | null): Promise<string[]>;
    /** Raw call to `/v1/chain/get_currency_stats` */
    get_currency_stats(code: string, symbol: string): Promise<GetCurrencyStatsResult>;
    /** Raw call to `/v1/chain/get_info` */
    get_info(): Promise<GetInfoResult>;
    /** Raw call to `/v1/chain/get_producer_schedule` */
    get_producer_schedule(): Promise<GetProducerScheduleResult>;
    /** Raw call to `/v1/chain/get_producers` */
    get_producers(json?: boolean, lowerBound?: string, limit?: number): Promise<GetProducersResult>;
    /** Raw call to `/v1/chain/get_raw_code_and_abi` */
    get_raw_code_and_abi(accountName: string): Promise<GetRawCodeAndAbiResult>;
    /** calls `/v1/chain/get_raw_code_and_abi` and pulls out unneeded raw wasm code */
    getRawAbi(accountName: string): Promise<BinaryAbi>;
    /** Raw call to `/v1/chain/get_raw_abi` */
    get_raw_abi(accountName: string): Promise<GetRawAbiResult>;
    /** Raw call to `/v1/chain/get_scheduled_transactions` */
    get_scheduled_transactions(json?: boolean, lowerBound?: string, limit?: number): Promise<GetScheduledTransactionsResult>;
    /** Raw call to `/v1/chain/get_table_rows` */
    get_table_rows({ json, code, scope, table, lower_bound, upper_bound, index_position, key_type, limit, reverse, show_payer, }: any): Promise<GetTableRowsResult>;
    /** Raw call to `/v1/chain/get_kv_table_rows` */
    get_kv_table_rows({ json, code, table, index_name, encode_type, index_value, lower_bound, upper_bound, limit, reverse, show_payer, }: any): Promise<GetTableRowsResult>;
    /** Raw call to `/v1/chain/get_table_by_scope` */
    get_table_by_scope({ code, table, lower_bound, upper_bound, limit, }: any): Promise<GetTableByScopeResult>;
    /** Get subset of `availableKeys` needed to meet authorities in `transaction`. Implements `AuthorityProvider` */
    getRequiredKeys(args: AuthorityProviderArgs): Promise<string[]>;
    /** Push a serialized transaction (replaced by send_transaction, but returned format has changed) */
    push_transaction({ signatures, compression, serializedTransaction, serializedContextFreeData, }: PushTransactionArgs): Promise<TransactResult>;
    /** Raw call to `/v1/chain/push_ro_transaction */
    push_ro_transaction({ signatures, compression, serializedTransaction }: PushTransactionArgs, returnFailureTraces?: boolean): Promise<ReadOnlyTransactResult>;
    push_transactions(transactions: PushTransactionArgs[]): Promise<TransactResult[]>;
    /** Send a serialized transaction */
    send_transaction({ signatures, compression, serializedTransaction, serializedContextFreeData, }: PushTransactionArgs): Promise<TransactResult>;
    /** Raw call to `/v1/db_size/get` */
    db_size_get(): Promise<DBSizeGetResult>;
    /** Raw call to `/v1/trace_api/get_block` */
    trace_get_block(block_num: number): Promise<TraceApiGetBlockResult>;
    /** Raw call to `/v1/history/get_actions` */
    history_get_actions(accountName: string, pos?: number | null, offset?: number | null): Promise<any>;
    /** Raw call to `/v1/history/get_transaction` */
    history_get_transaction(id: string, blockNumHint?: number | null): Promise<NativeTransaction>;
    /** Raw call to `/v1/history/get_key_accounts` */
    history_get_key_accounts(publicKey: string): Promise<any>;
    /** Raw call to `/v1/history/get_controlled_accounts` */
    history_get_controlled_accounts(controllingAccount: string): Promise<any>;
    /** FIO` */
    get_nfts_fio_address(address: string): Promise<any>;
    /** Proton` */
    isLightKYCVerified: typeof isLightKYCVerified;
    getValidKycProviders: typeof getValidKycProviders;
    fetchCredentials: typeof fetchCredentials;
}

declare class Api {
    /** Issues RPC calls */
    rpc: JsonRpc;
    /** Get subset of `availableKeys` needed to meet authorities in a `transaction` */
    authorityProvider: AuthorityProvider;
    /** Supplies ABIs in raw form (binary) */
    abiProvider: AbiProvider;
    /** Signs transactions */
    signatureProvider?: SignatureProvider;
    /** Converts abi files between binary and structured form (`abi.abi.json`) */
    abiTypes: Map<string, Type>;
    /** Converts transactions between binary and structured form (`transaction.abi.json`) */
    transactionTypes: Map<string, Type>;
    /** Holds information needed to serialize contract actions */
    contracts: Map<string, Contract>;
    /** Fetched abis */
    cachedAbis: Map<string, CachedAbi>;
    /** Crypto */
    crypto?: Crypto;
    recoverPersonalSignature?: RecoverPersonalSignature;
    /**
     * @param args
     *    * `rpc`: Issues RPC calls
     *    * `authorityProvider`: Get public keys needed to meet authorities in a transaction
     *    * `abiProvider`: Supplies ABIs in raw form (binary)
     *    * `signatureProvider`: Signs transactions
     */
    constructor(args: {
        rpc: JsonRpc;
        authorityProvider?: AuthorityProvider;
        abiProvider?: AbiProvider;
        signatureProvider?: SignatureProvider;
        crypto?: Crypto;
        recoverPersonalSignature?: RecoverPersonalSignature;
    });
    getCrypto(): Crypto;
    getRecoverPersonalSignature(): RecoverPersonalSignature;
    /** Decodes an abi as Uint8Array into json. */
    rawAbiToJson(rawAbi: Uint8Array): Abi;
    /** Encodes a json abi as Uint8Array. */
    jsonToRawAbi(jsonAbi: Abi): Uint8Array;
    /** Get abi in both binary and structured forms. Fetch when needed. */
    getCachedAbi(accountName: string, reload?: boolean): Promise<CachedAbi>;
    /** Get abi in structured form. Fetch when needed. */
    getAbi(accountName: string, reload?: boolean): Promise<Abi>;
    /** Get abis needed by a transaction */
    getTransactionAbis(transaction: any, reload?: boolean): Promise<BinaryAbi[]>;
    /** Get data needed to serialize actions in a contract */
    getContract(accountName: string, reload?: boolean): Promise<Contract>;
    /** Convert `value` to binary form. `type` must be a built-in abi type or in `transaction.abi.json`. */
    serialize(buffer: SerialBuffer, type: string, value: any): void;
    /** Convert data in `buffer` to structured form. `type` must be a built-in abi type or in `transaction.abi.json`. */
    deserialize(buffer: SerialBuffer, type: string): any;
    /** Convert a transaction to binary */
    serializeTransaction(transaction: Transaction): Uint8Array;
    /** Serialize context-free data */
    serializeContextFreeData(contextFreeData?: Uint8Array[]): Uint8Array | undefined;
    /** Convert a transaction from binary. Leaves actions in hex. */
    deserializeTransaction(transaction: Uint8Array): Transaction;
    private transactionExtensions;
    serializeTransactionExtensions(transaction: Transaction): [number, string][];
    deserializeTransactionExtensions(data: [number, string][]): any[];
    deleteTransactionExtensionObjects(transaction: Transaction): Transaction;
    /** Convert actions to hex */
    serializeActions(actions: Action[]): Promise<SerializedAction[]>;
    /** Convert actions from hex */
    deserializeActions(actions: Action[]): Promise<Action[]>;
    deserializeActionsSync(actions?: Action[]): Promise<Action[]>;
    deserializeActionsSyncWithAbi(actions?: Action[]): Promise<Action[]>;
    /** Convert a transaction from binary. Also deserializes actions. */
    serializeTransactionWithActions(transaction: Transaction): Promise<{
        serializedTransaction: Uint8Array;
        serializedContextFreeData: Uint8Array | undefined;
    }>;
    /** Convert a transaction from binary. Also deserializes actions. */
    deserializeTransactionWithActions(transaction: Uint8Array | string): Promise<any>;
    /** Deflate a serialized object */
    deflateSerializedArray(serializedArray: Uint8Array): Uint8Array;
    /** Inflate a compressed serialized object */
    inflateSerializedArray(compressedSerializedArray: Uint8Array): Uint8Array;
    /**
     * Create and optionally broadcast a transaction.
     *
     * Named Parameters:
     * `broadcast`: broadcast this transaction?
     * `sign`: sign this transaction?
     * `compression`: compress this transaction?
     * `readOnlyTrx`: read only transaction?
     * `returnFailureTraces`: return failure traces? (only available for read only transactions currently)
     *
     * If both `blocksBehind` and `expireSeconds` are present,
     * then fetch the block which is `blocksBehind` behind head block,
     * use it as a reference for TAPoS, and expire the transaction `expireSeconds` after that block's time.
     *
     * If both `useLastIrreversible` and `expireSeconds` are present,
     * then fetch the last irreversible block, use it as a reference for TAPoS,
     * and expire the transaction `expireSeconds` after that block's time.
     *
     * @returns node response if `broadcast`, `{signatures, serializedTransaction}` if `!broadcast`
     */
    transact(transaction: Transaction, { broadcast, sign, readOnlyTrx, returnFailureTraces, requiredKeys, // When you will sign later
    compression, blocksBehind, useLastIrreversible, expireSeconds, transactionHeader, }?: TransactConfig): Promise<TransactResult | ReadOnlyTransactResult | PushTransactionArgs>;
    transactWithDelay(transaction: any, params: TransactConfig | undefined, delay: number): Promise<any>;
    query(account: string, short: boolean, query: Query, { sign, requiredKeys, authorization }: QueryConfig): Promise<any>;
    /** Broadcast a signed transaction */
    pushSignedTransaction({ signatures, serializedTransaction, serializedContextFreeData, }: PushTransactionArgs, readOnlyTrx?: boolean, returnFailureTraces?: boolean): Promise<TransactResult | ReadOnlyTransactResult>;
    pushCompressedSignedTransaction({ signatures, serializedTransaction, serializedContextFreeData, }: PushTransactionArgs, readOnlyTrx?: boolean, returnFailureTraces?: boolean): Promise<TransactResult | ReadOnlyTransactResult>;
    generateTapos(info: GetInfoResult | undefined, transaction: Transaction, blocksBehind: number | undefined, useLastIrreversible: boolean | undefined, expireSeconds: number): Promise<{
        expiration: string;
        ref_block_num: number;
        ref_block_prefix: number;
        max_net_usage_words?: number | undefined;
        max_cpu_usage_ms?: number | undefined;
        delay_sec?: number | undefined;
        context_free_actions?: Action[] | undefined;
        context_free_data?: Uint8Array[] | undefined;
        actions: Action[];
        transaction_extensions?: [number, string][] | undefined;
        resource_payer?: ResourcePayer | undefined;
    }>;
    private hasRequiredTaposFields;
    private tryGetBlockHeaderState;
    private tryGetBlockInfo;
    private tryRefBlockFromGetInfo;
    with(accountName: string): ActionBuilder;
    buildTransaction(cb?: (tx: TransactionBuilder) => void): TransactionBuilder | void;
    getAccountKeys(actor: string, permission: string): Promise<string[]>;
    sha256Digest(array: Uint8Array | ArrayBuffer): Promise<Uint8Array>;
    matchRsaKeyToSignature({ action, credentials, }: {
        credentials: WaKey[];
        action: WaExecAction;
    }): Promise<boolean>;
    matchEthKeyToSignature({ action, credentials, }: {
        credentials: WaKey[];
        action: WaExecAction;
    }): Promise<boolean>;
    checkIfKeysMatchWaAction({ actor, permission, action, }: {
        actor: string;
        permission: string;
        action: WaExecAction;
    }): Promise<boolean>;
    checkIfKeysMatchTransaction({ actor, permission, transaction, signatures, chainId, }: {
        actor: string;
        permission: string;
        transaction: Transaction;
        signatures: string[];
        chainId?: string;
    }): Promise<boolean>;
}
declare class TransactionBuilder {
    private api;
    private actions;
    private contextFreeGroups;
    constructor(api: Api);
    with(accountName: string): ActionBuilder;
    associateContextFree(contextFreeGroup: ContextFreeGroupCallback): TransactionBuilder;
    send(config?: TransactConfig): Promise<PushTransactionArgs | ReadOnlyTransactResult | TransactResult>;
}
declare class ActionBuilder {
    private api;
    private readonly accountName;
    serializedData: SerializedAction | undefined;
    constructor(api: Api, accountName: string);
    as(actorName?: string | Authorization[]): ActionSerializerType;
}

/** Is `bignum` a negative number? */
declare const isNegative: (bignum: Uint8Array) => boolean;
/** Negate `bignum` */
declare const negate: (bignum: Uint8Array) => void;
/**
 * Convert an unsigned decimal number in `s` to a bignum
 *
 * @param size bignum size (bytes)
 */
declare const decimalToBinary: (size: number, s: string) => Uint8Array;
/**
 * Convert a signed decimal number in `s` to a bignum
 *
 * @param size bignum size (bytes)
 */
declare const signedDecimalToBinary: (size: number, s: string) => Uint8Array;
/**
 * Convert `bignum` to an unsigned decimal number
 *
 * @param minDigits 0-pad result to this many digits
 */
declare const binaryToDecimal: (bignum: Uint8Array, minDigits?: number) => string;
/**
 * Convert `bignum` to a signed decimal number
 *
 * @param minDigits 0-pad result to this many digits
 */
declare const signedBinaryToDecimal: (bignum: Uint8Array, minDigits?: number) => string;
/**
 * Convert an unsigned base-58 number in `s` to a bignum
 *
 * @param size bignum size (bytes)
 */
declare const base58ToBinary: (size: number, s: string) => Uint8Array;
/**
 * Convert `bignum` to a base-58 number
 *
 * @param minDigits 0-pad result to this many digits
 */
declare const binaryToBase58: (bignum: Uint8Array) => string;
/** Convert an unsigned base-64 number in `s` to a bignum */
declare const base64ToBinary: (s: string) => Uint8Array;
/** Key types this library supports */
declare enum KeyType {
    k1 = 0,
    r1 = 1,
    wa = 2,
    rsa = 100,
    eth = 101
}
/** Public key data size, excluding type field */
declare const publicKeyDataSize = 33;
/** Private key data size, excluding type field */
declare const privateKeyDataSize = 32;
/** Signature data size, excluding type field */
declare const signatureDataSize = 65;
/** Public key, private key, or signature in binary form */
interface Key$1 {
    type: KeyType;
    data: Uint8Array;
}
/** Convert key in `s` to binary form */
declare const stringToPublicKey: (s: string, prefix?: string) => Key$1;
/** Convert public `key` to legacy string (base-58) form */
declare const publicKeyToLegacyString: (key: Key$1, prefix?: string) => string;
/** Convert `key` to string (base-58) form */
declare const publicKeyToString: (key: Key$1) => string;
/** If a key is in the legacy format (`EOS` prefix), then convert it to the new format (`PUB_K1_`).
 * Leaves other formats untouched
 */
declare const convertLegacyPublicKey: (s: string, prefix?: string) => string;
/** If a key is in the legacy format (`EOS` prefix), then convert it to the new format (`PUB_K1_`).
 * Leaves other formats untouched
 */
declare const convertLegacyPublicKeys: (keys: string[], prefix?: string) => string[];
/** Convert key in `s` to binary form. */
declare const stringToPrivateKey: (s: string) => Key$1;
/** Convert private `key` to legacy string (base-58) form */
declare const privateKeyToLegacyString: (key: Key$1) => string;
/** Convert `key` to string (base-58) form */
declare const privateKeyToString: (key: Key$1) => string;
/** Convert key in `s` to binary form */
declare const stringToSignature: (s: string) => Key$1;
/** Convert `signature` to string (base-58) form */
declare const signatureToString: (signature: Key$1) => string;

declare const Numeric_isNegative: typeof isNegative;
declare const Numeric_negate: typeof negate;
declare const Numeric_decimalToBinary: typeof decimalToBinary;
declare const Numeric_signedDecimalToBinary: typeof signedDecimalToBinary;
declare const Numeric_binaryToDecimal: typeof binaryToDecimal;
declare const Numeric_signedBinaryToDecimal: typeof signedBinaryToDecimal;
declare const Numeric_base58ToBinary: typeof base58ToBinary;
declare const Numeric_binaryToBase58: typeof binaryToBase58;
declare const Numeric_base64ToBinary: typeof base64ToBinary;
type Numeric_KeyType = KeyType;
declare const Numeric_KeyType: typeof KeyType;
declare const Numeric_publicKeyDataSize: typeof publicKeyDataSize;
declare const Numeric_privateKeyDataSize: typeof privateKeyDataSize;
declare const Numeric_signatureDataSize: typeof signatureDataSize;
declare const Numeric_stringToPublicKey: typeof stringToPublicKey;
declare const Numeric_publicKeyToLegacyString: typeof publicKeyToLegacyString;
declare const Numeric_publicKeyToString: typeof publicKeyToString;
declare const Numeric_convertLegacyPublicKey: typeof convertLegacyPublicKey;
declare const Numeric_convertLegacyPublicKeys: typeof convertLegacyPublicKeys;
declare const Numeric_stringToPrivateKey: typeof stringToPrivateKey;
declare const Numeric_privateKeyToLegacyString: typeof privateKeyToLegacyString;
declare const Numeric_privateKeyToString: typeof privateKeyToString;
declare const Numeric_stringToSignature: typeof stringToSignature;
declare const Numeric_signatureToString: typeof signatureToString;
declare namespace Numeric {
  export {
    Numeric_isNegative as isNegative,
    Numeric_negate as negate,
    Numeric_decimalToBinary as decimalToBinary,
    Numeric_signedDecimalToBinary as signedDecimalToBinary,
    Numeric_binaryToDecimal as binaryToDecimal,
    Numeric_signedBinaryToDecimal as signedBinaryToDecimal,
    Numeric_base58ToBinary as base58ToBinary,
    Numeric_binaryToBase58 as binaryToBase58,
    Numeric_base64ToBinary as base64ToBinary,
    Numeric_KeyType as KeyType,
    Numeric_publicKeyDataSize as publicKeyDataSize,
    Numeric_privateKeyDataSize as privateKeyDataSize,
    Numeric_signatureDataSize as signatureDataSize,
    Key$1 as Key,
    Numeric_stringToPublicKey as stringToPublicKey,
    Numeric_publicKeyToLegacyString as publicKeyToLegacyString,
    Numeric_publicKeyToString as publicKeyToString,
    Numeric_convertLegacyPublicKey as convertLegacyPublicKey,
    Numeric_convertLegacyPublicKeys as convertLegacyPublicKeys,
    Numeric_stringToPrivateKey as stringToPrivateKey,
    Numeric_privateKeyToLegacyString as privateKeyToLegacyString,
    Numeric_privateKeyToString as privateKeyToString,
    Numeric_stringToSignature as stringToSignature,
    Numeric_signatureToString as signatureToString,
  };
}

declare const sha256: (data: string | Buffer) => string;

/** Represents/stores a public key and provides easy conversion for use with `elliptic` lib */
declare class PublicKey {
    key: Key$1;
    ec: ec;
    constructor(key: Key$1);
    /** Instantiate public key from an EOSIO-format public key */
    static fromString(publicKeyStr: string): PublicKey;
    /** Instantiate public key from an `elliptic`-format public key */
    static fromElliptic(publicKey: ec.KeyPair, keyType: KeyType): PublicKey;
    static equal(pk1: PublicKey, pk2: PublicKey): boolean;
    /** Export public key as EOSIO-format public key */
    toString(): string;
    /** Export public key as Legacy EOSIO-format public key */
    toLegacyString(prefix?: string): string;
    /** Export public key as `elliptic`-format public key */
    toElliptic(): ec.KeyPair;
    /** Get key type from key */
    getType(): KeyType;
    /** Validate a public key */
    isValid(): boolean;
}

/** Represents/stores a Signature and provides easy conversion for use with `elliptic` lib */
declare class Signature {
    private signature;
    ec: ec;
    constructor(signature: Key$1);
    /** Instantiate Signature from an EOSIO-format Signature */
    static fromString(sig: string): Signature;
    /** Instantiate Signature from an `elliptic`-format Signature */
    static fromElliptic(ellipticSig: ec.Signature, keyType: KeyType): Signature;
    /** Export Signature as `elliptic`-format Signature
     * NOTE: This isn't an actual elliptic-format Signature, as ec.Signature is not exported by the library.
     * That's also why the return type is `any`.  We're *actually* returning an object with the 3 params
     * not an ec.Signature.
     * Further NOTE: @types/elliptic shows ec.Signature as exported; it is *not*.  Hence the `any`.
     */
    toElliptic(): any;
    /** Export Signature as EOSIO-format Signature */
    toString(): string;
    /** Export Signature in binary format */
    toBinary(): Uint8Array;
    /** Get key type from signature */
    getType(): KeyType;
    /** Get EC */
    getEc(): ec;
    /** Verify a signature with a message or hashed message digest and public key */
    verify(data: BNInput, publicKey: PublicKey, shouldHash?: boolean, encoding?: BufferEncoding): boolean;
    /** Recover a public key from a message or hashed message digest and signature */
    recover(data: BNInput, shouldHash?: boolean, encoding?: BufferEncoding): PublicKey;
}

/** Represents/stores a private key and provides easy conversion for use with `elliptic` lib */
declare class PrivateKey {
    private key;
    ec: ec;
    constructor(key: Key$1);
    /** Instantiate private key from an `elliptic`-format private key */
    static fromElliptic(privKey: ec.KeyPair, keyType: KeyType): PrivateKey;
    /** Instantiate private key from an EOSIO-format private key */
    static fromString(keyString: string): PrivateKey;
    /** Export private key as `elliptic`-format private key */
    toElliptic(): ec.KeyPair;
    toLegacyString(): string;
    /** Export private key as EOSIO-format private key */
    toString(): string;
    /** Get key type from key */
    getType(): KeyType;
    /** Retrieve the public key from a private key */
    getPublicKey(): PublicKey;
    /** Sign a message or hashed message digest with private key */
    sign(data: BNInput, shouldHash?: boolean, encoding?: BufferEncoding): Signature;
    /** Validate a private key */
    isValid(): boolean;
}

/** expensive to construct; so we do it once and reuse it */
declare const k1Ec: ec;
declare const r1Ec: ec;
/** Construct the elliptic curve object based on key type */
declare const constructElliptic: (type: KeyType) => ec;
declare const generateKeyPair: (type: KeyType, options?: {
    secureEnv?: boolean;
    ecOptions?: ec.GenKeyPairOptions;
}) => {
    publicKey: PublicKey;
    privateKey: PrivateKey;
};

declare const Key_k1Ec: typeof k1Ec;
declare const Key_r1Ec: typeof r1Ec;
declare const Key_constructElliptic: typeof constructElliptic;
declare const Key_generateKeyPair: typeof generateKeyPair;
type Key_PrivateKey = PrivateKey;
declare const Key_PrivateKey: typeof PrivateKey;
type Key_PublicKey = PublicKey;
declare const Key_PublicKey: typeof PublicKey;
type Key_Signature = Signature;
declare const Key_Signature: typeof Signature;
declare namespace Key {
  export {
    Key_k1Ec as k1Ec,
    Key_r1Ec as r1Ec,
    Key_constructElliptic as constructElliptic,
    Key_generateKeyPair as generateKeyPair,
    Key_PrivateKey as PrivateKey,
    Key_PublicKey as PublicKey,
    Key_Signature as Signature,
  };
}

/**
 * @module JS-Sig
 */

/** Construct the digest from transaction details */
declare const digestFromSerializedData: (chainId: string, serializedTransaction: Uint8Array, serializedContextFreeData?: Uint8Array, e?: ec) => any;
/** Signs transactions using in-process private keys */
declare class JsSignatureProvider implements SignatureProvider {
    /** map public to private keys */
    keys: Map<string, ec.KeyPair>;
    /** public keys */
    availableKeys: string[];
    /** @param privateKeys private keys to sign with */
    constructor(privateKeys: string[]);
    /** Public keys associated with the private keys that the `SignatureProvider` holds */
    getAvailableKeys(): Promise<string[]>;
    /** Sign a transaction */
    sign({ chainId, requiredKeys, serializedTransaction, serializedContextFreeData, }: SignatureProviderArgs): Promise<{
        signatures: string[];
        serializedTransaction: Uint8Array;
        serializedContextFreeData: Uint8Array | undefined;
    }>;
}

declare const _default: {
    Api: typeof Api;
    ApiInterfaces: typeof ApiInterfaces;
    JsonRpc: typeof JsonRpc;
    Numeric: typeof Numeric;
    RpcInterfaces: typeof RpcInterfaces;
    RpcError: typeof RpcError;
    Serialize: typeof Serialize;
    JsSignatureProvider: typeof JsSignatureProvider;
    Key: typeof Key;
    sha256: (data: string | Buffer) => string;
};

export { Api, ApiInterfaces, JsSignatureProvider, JsonRpc, Key, Numeric, RpcError, RpcInterfaces, Serialize, _default as default, digestFromSerializedData, sha256 };
