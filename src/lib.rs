mod memory;
mod scan;

use pyo3::prelude::*;
use std::collections::HashMap;
use memory::Process;
use scan::{Scan, Scannable};
use winapi::um::winnt;
use str;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

pub struct ProcessItem {
    pid: u32,
    name: String,
}

pub fn ret_scan(search: String) -> Result<Scan<Box<dyn Scannable>>, ()> {
    let value = search;
    value.parse()
}

fn vec_to_arr<T, const N: usize>(v: Vec<T>) -> [T; N] {
    v.try_into()
        .unwrap_or_else(|v: Vec<T>| panic!("Expected a Vec of length {} but it was {}", N, v.len()))
}

#[pyfunction]
fn initialize() -> Py<PyAny> {
    let mut addrs: HashMap<String,usize> = HashMap::new();

    let processes = memory::enum_proc()
        .unwrap()
        .into_iter()
        .flat_map(memory::Process::open)
        .flat_map(|proc| match proc.name() {
            Ok(name) => Ok(ProcessItem {
                pid: proc.pid(),
                name,
            }),
            Err(err) => Err(err),
        })
        .collect::<Vec<_>>();

    let mut bloons_pid: u32 = 0;

    for p in processes.into_iter() {
        if p.name == "BloonsTD6.exe" {
            bloons_pid = p.pid;
        }
    }

    println!("Pid: {}", bloons_pid);

    let process = Process::open(bloons_pid).unwrap();
    println!("Opened process {:?}", process);

    let mask = winnt::PAGE_EXECUTE_READWRITE
        | winnt::PAGE_EXECUTE_WRITECOPY
        | winnt::PAGE_READWRITE
        | winnt::PAGE_WRITECOPY;

    let regions = process
        .memory_regions()
        .into_iter()
        .filter(|p| (p.Protect & mask) != 0)
        .collect::<Vec<_>>();

    println!("Scanning {} memory regions", regions.len());
    let scan = ret_scan("650.0f64".to_owned()).unwrap();
    let last_scan = process.scan_regions(&regions, scan);
    let cash_addr = last_scan
        .iter()
        .flat_map(|r| r.locations.iter())
        .next()
        .unwrap();
    println!(
        "Address of Money: {:#02X}",
        cash_addr
    );

    addrs.insert(
        "cash".to_string(), cash_addr
    );

    let mut search: String = (cash_addr-40).to_string();
    let borrowed_string: &str = "u64";
    search.push_str(borrowed_string);
    let scan = ret_scan(search.to_owned()).unwrap();
    let last_scan = process.scan_regions(&regions, scan);
    let inter_addr = last_scan
        .iter()
        .flat_map(|r| r.locations.iter())
        .next()
        .unwrap();

    println!(
        "Intermediate Address: {:#02X}",
        inter_addr
    );

    search = (inter_addr-16).to_string();
    search.push_str(borrowed_string);
    let scan = ret_scan(search.to_owned()).unwrap();
    let last_scan = process.scan_regions(&regions, scan);
    let inter_addr = last_scan
        .iter()
        .flat_map(|r| r.locations.iter())
        .next()
        .unwrap();

    println!(
        "Intermediate Address: {:#02X}",
        inter_addr
    );

    search = (inter_addr-48).to_string();
    search.push_str(borrowed_string);
    let scan = ret_scan(search.to_owned()).unwrap();
    let last_scan = process.scan_regions(&regions, scan);
    let inter_addr = last_scan
        .iter()
        .flat_map(|r| r.locations.iter())
        .next()
        .unwrap();

    println!(
        "Intermediate Address: {:#02X}",
        inter_addr
    );

    search = (inter_addr-24).to_string();
    search.push_str(borrowed_string);
    let scan = ret_scan(search.to_owned()).unwrap();
    let last_scan = process.scan_regions(&regions, scan);
    let inter_addr = last_scan
        .iter()
        .flat_map(|r| r.locations.iter())
        .next()
        .unwrap();

    println!(
        "Intermediate Address: {:#02X}",
        inter_addr
    );

    let game_addr: usize = inter_addr-696;

    // Numbers are decimal
    // health: game_addr+720 -> +40 (double)
    // towercount: game_addr+128-> +24 -> +48 -> +16 (int32)
    // round-1: game_addr+728-> +144 -> +224 -> +40 (double?)

    // FINDING HEALTH ADDRESS
    let inter_addr: usize = game_addr+720;
    println!(
        "Intermediate Address: {:#02X}",
        inter_addr
    );

    let res_addr_vec = process.read_memory(inter_addr, 8).unwrap();
    let health_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
    println!(
        "Health Address: {:#02X}",
        health_addr+40
    );

    addrs.insert(
        "health".to_string(), health_addr+40
    );

    // FINDING TOWERCOUNT ADDRESS
    let inter_addr: usize = game_addr+128;
    let res_addr_vec = process.read_memory(inter_addr, 8).unwrap();
    let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
    let res_addr_vec = process.read_memory(inter_addr+24, 8).unwrap();
    let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
    let res_addr_vec = process.read_memory(inter_addr+48, 8).unwrap();
    let tower_count_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));

    println!(
        "Tower Count Address: {:#02X}",
        tower_count_addr+16
    );

    addrs.insert(
        "tower_count".to_string(), tower_count_addr+16
    );


    // FINDING ROUND ADDRESS
    let inter_addr: usize = game_addr+728;
    let res_addr_vec = process.read_memory(inter_addr, 8).unwrap();
    let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
    let res_addr_vec = process.read_memory(inter_addr+144, 8).unwrap();
    let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
    let res_addr_vec = process.read_memory(inter_addr+224, 8).unwrap();
    let round_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));

    println!(
        "Round Address: {:#02X}",
        round_addr+40
    );

    addrs.insert(
        "round".to_string(), round_addr+40
    );


    return Python::with_gil(|py: Python| {
        addrs.to_object(py)
    });
}

#[pyfunction]
fn get_value_double(addr: usize, val: usize) -> PyResult<f64> {
    let processes = memory::enum_proc()
        .unwrap()
        .into_iter()
        .flat_map(memory::Process::open)
        .flat_map(|proc| match proc.name() {
            Ok(name) => Ok(ProcessItem {
                pid: proc.pid(),
                name,
            }),
            Err(err) => Err(err),
        })
        .collect::<Vec<_>>();

    let mut bloons_pid: u32 = 0;

    for p in processes.into_iter() {
        if p.name == "BloonsTD6.exe" {
            bloons_pid = p.pid;
        }
    }

    let process = Process::open(bloons_pid).unwrap();

    let res_addr_vec = process.read_memory(addr, val).unwrap();
    let value: f64 = f64::from_le_bytes(vec_to_arr(res_addr_vec));

    println!(
        "Value: {}",
        value
    );

    Ok(value)
}


#[pyfunction]
fn get_value_int(addr: usize, val:usize) -> PyResult<i32> {
    let processes = memory::enum_proc()
        .unwrap()
        .into_iter()
        .flat_map(memory::Process::open)
        .flat_map(|proc| match proc.name() {
            Ok(name) => Ok(ProcessItem {
                pid: proc.pid(),
                name,
            }),
            Err(err) => Err(err),
        })
        .collect::<Vec<_>>();

    let mut bloons_pid: u32 = 0;

    for p in processes.into_iter() {
        if p.name == "BloonsTD6.exe" {
            bloons_pid = p.pid;
        }
    }

    let process = Process::open(bloons_pid).unwrap();

    let res_addr_vec = process.read_memory(addr, val).unwrap();
    let value: i32 = i32::from_be_bytes(vec_to_arr(res_addr_vec));

    println!(
        "Value: {}",
        value
    );

    Ok(value)
}

/// A Python module implemented in Rust.
#[pymodule]
fn BloonsAI(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(get_value_double, m)?)?;
    m.add_function(wrap_pyfunction!(get_value_int, m)?)?;
    Ok(())
}