mod memory;
mod scan;

use pyo3::prelude::*;
use std::collections::HashMap;
use memory::Process;
use scan::{Scan, Scannable};
use winapi::um::winnt;
use str;
use std::fs::File;
use std::fs;
use std::path::Path;
use std::io::{BufRead, BufReader, Write};
use std::{thread, time};
use std::num::Wrapping;

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

fn get_addrs(addr: usize, offset: usize, process: &Process, regions: &Vec<winnt::MEMORY_BASIC_INFORMATION>) -> Vec<usize> {
    let mut addrs: Vec<usize> = Vec::new();
    let mut search: String;
    let borrowed_string: &str = "u64";
    search = (addr-offset).to_string();
    search.push_str(borrowed_string);
    let scan = ret_scan(search.to_owned()).unwrap();
    let last_scan = process.scan_regions(&regions, scan);

    for r in last_scan.iter() {
        for l in r.locations.iter() {
            addrs.push(l);
        }
    }

    return addrs;
}

fn get_health_addr(game_addr: usize, process: &Process) -> usize {
    let inter_addr: usize = game_addr+720;

    if let Ok(res_addr_vec) = process.read_memory(inter_addr, 8){
        let health_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec)).wrapping_add(40);
        
        println!(
            "Health Address: {:#02X}",
            health_addr
        );
    
        return health_addr;
    }
    
    return 0;
}

fn get_tower_count_addr(game_addr: usize, process: &Process) -> usize {
    let inter_addr: usize = game_addr+128;
    if let Ok(res_addr_vec) = process.read_memory(inter_addr, 8){
        let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
        if let Ok(res_addr_vec) = process.read_memory(inter_addr+24, 8){
            let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
            if let Ok(res_addr_vec) = process.read_memory(inter_addr+48, 8){
                let tower_count_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec)).wrapping_add(16);
                println!(
                    "Tower Count Address: {:#02X}",
                    tower_count_addr
                );
            
                return tower_count_addr;
            }
        }
    }
    return 0;
}

fn get_round_addr(game_addr: usize, process: &Process) -> usize {
    let inter_addr: usize = game_addr+728;
    if let Ok(res_addr_vec) = process.read_memory(inter_addr, 8){
        let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
        if let Ok(res_addr_vec) = process.read_memory(inter_addr+144, 8){
            let inter_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec));
            if let Ok(res_addr_vec) = process.read_memory(inter_addr+224, 8){
                let round_addr: usize = usize::from_le_bytes(vec_to_arr(res_addr_vec)).wrapping_add(40);
                println!(
                    "Round Address: {:#02X}",
                    round_addr
                );
            
                return round_addr;
            }
        }
    }
    return 0;
}

#[pyfunction]
fn initialize() -> Py<PyAny> {
    let mut addrs: HashMap<String,usize> = HashMap::new();

    let path = Path::new("cache.txt");
    
    if(path.exists()){
        let file = File::open(&path).unwrap();
        let reader = BufReader::new(file);
        for (index, line) in reader.lines().enumerate(){
            let line = line.unwrap();
            let items: Vec<&str> = line.split(" ").collect();
            addrs.insert(
                items[0].to_string(), items[1].parse::<usize>().unwrap()
            );
        }

        return Python::with_gil(|py: Python| {
            addrs.to_object(py)
        });
        
    } else {
        println!("No Cache, beginning search");
    }

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

    for i in 0..10 {
        println!("{}", 10-i);
        thread::sleep(time::Duration::from_secs(1));
    }

    let game_addr: usize = inter_addr-696;

    // Numbers are decimal
    // health: game_addr+720 -> +40 (double)
    // towercount: game_addr+128-> +24 -> +48 -> +16 (int32)
    // round-1: game_addr+728-> +144 -> +224 -> +40 (double?)

    // FINDING HEALTH ADDRESS
    let inter_addr: usize = game_addr+720;

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

    let mut file = File::create("cache.txt").unwrap();

    for (key, value) in addrs.iter() {
        let v = vec![key.to_string(), " ".to_string(), value.to_string()];
        let line = v.concat();
        writeln!(file, "{}", line);
    }

    return Python::with_gil(|py: Python| {
        addrs.to_object(py)
    });
}

#[pyfunction]
fn initialize_restart(health_amount: f64) -> Py<PyAny> {
    let mut addrs: HashMap<String,usize> = HashMap::new();

    let path = Path::new("cache.txt");
    
    if(path.exists()){
        fs::remove_file("cache.txt");
        println!("Cache deleted successfully!");
    } else {
        println!("No Cache");
    }

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

    let mut cash_addrs: Vec<usize> = Vec::new();
    let scan = ret_scan("650.0f64".to_owned()).unwrap();
    let last_scan = process.scan_regions(&regions, scan);

    for r in last_scan.iter() {
        for l in r.locations.iter() {
            cash_addrs.push(l);
        }
    }
    println!(
        "Cash Addresses: {}",
        cash_addrs.len()
    );

    let mut cash_addr: usize = 0;

    let mut inter_addrs1: Vec<usize> = Vec::new();
    let mut inter_addrs2: Vec<usize> = Vec::new();
    let mut inter_addrs3: Vec<usize> = Vec::new();
    let mut inter_addrs4: Vec<usize> = Vec::new();


    for addr1 in cash_addrs.iter(){
        println!(
            "Potential Address of Money: {:#02X}",
            addr1
        );
        inter_addrs1.clear();
        let mut inter_addr: usize = 0;
        inter_addrs1 = get_addrs(*addr1, 40, &process, &regions);
        
        if inter_addrs1.len() == 0 {
            println!(
                "Wrong Address - Trying Again"
            );
            continue;
        }

        cash_addr = *addr1;

        println!(
            "Intermediate Addresses: {}",
            inter_addrs1.len()
        );

        inter_addrs2.clear();

        for addr2 in inter_addrs1.iter() {
            println!(
                "Handling Address: {:#02X}",
                *addr2
            );
            inter_addrs2 = get_addrs(*addr2, 16, &process, &regions);
            if inter_addrs2.len() == 0 {
                println!(
                    "Wrong Address - Trying Again"
                );
                continue;
           }

            println!(
                "Intermediate Addresses: {}",
                inter_addrs2.len()
            );

            inter_addrs3.clear();

            for addr3 in inter_addrs2.iter(){
                println!(
                    "Handling Address: {:#02X}",
                    *addr3
                );
                inter_addrs3 = get_addrs(*addr3, 48, &process, &regions);
                if inter_addrs3.len() == 0 {
                    println!(
                        "Wrong Address - Trying Again"
                    );
                    continue;
                }

                println!(
                    "Intermediate Addresses: {}",
                    inter_addrs3.len()
                );

                inter_addrs4.clear();

                for addr4 in inter_addrs3.iter(){
                    println!(
                        "Handling Address: {:#02X}",
                        *addr4
                    );
                    inter_addrs4 = get_addrs(*addr4, 24, &process, &regions);
                    if inter_addrs4.len() == 0 {
                        println!(
                            "Wrong Address - Trying Again"
                        );
                        continue;
                    }

                    println!(
                        "Intermediate Addresses: {}",
                        inter_addrs4.len()
                    );

                    for potential_addr in inter_addrs4.iter(){
                        // Potential game_addr + 696
                        inter_addr = *potential_addr;
                        println!(
                            "Intermediate Address: {:#02X}",
                            inter_addr
                        );

                        let game_addr: usize = inter_addr-696;
                        println!(
                            "Possible Game Address: {:#02X} - Confirming Now",
                            game_addr
                        );

                        // Numbers are decimal
                        // health: game_addr+720 -> +40 (double)
                        // towercount: game_addr+128-> +24 -> +48 -> +16 (int32)
                        // round-1: game_addr+728-> +144 -> +224 -> +40 (double)

                        let health_addr = get_health_addr(game_addr, &process);
                        let round_addr = get_round_addr(game_addr, &process);
                        let tower_count_addr = get_tower_count_addr(game_addr, &process);

                        if(health_addr == 0 || round_addr == 0 || tower_count_addr == 0){
                            println!(
                                "Incorrect Game Address (Wrong Addresses) - Trying Again"
                            );
                            continue;
                        }

                        let mut health_value = -1.0;
                        let mut round_value = -1.0;
                        let mut tower_count_value = -1.0;

                        if let Ok(res_addr_vec) = process.read_memory(health_addr, 8){
                            health_value = f64::from_le_bytes(vec_to_arr(res_addr_vec));
                        }
                        

                        if let Ok(res_addr_vec) = process.read_memory(round_addr, 8){
                            round_value = f64::from_le_bytes(vec_to_arr(res_addr_vec));
                        }
                       

                        if let Ok(res_addr_vec) = process.read_memory(tower_count_addr, 4){
                            tower_count_value = i32::from_le_bytes(vec_to_arr(res_addr_vec)) as f64;
                        }
                       

                        if health_value != health_amount || round_value != 0.0 || tower_count_value != 0.0 {
                            println!(
                                "Incorrect Game Address (Wrong Values) - Trying Again"
                            );
                            continue;
                        }

                        addrs.insert(
                            "cash".to_string(), cash_addr
                        );

                        addrs.insert(
                            "health".to_string(), health_addr
                        );
                    
                        addrs.insert(
                            "tower_count".to_string(), tower_count_addr
                        );
                    
                        addrs.insert(
                            "round".to_string(), round_addr
                        );

                        let mut file = File::create("cache.txt").unwrap();

                        for (key, value) in addrs.iter() {
                            let v = vec![key.to_string(), " ".to_string(), value.to_string()];
                            let line = v.concat();
                            writeln!(file, "{}", line);
                        }

                        println!(
                            "Confirmed Game Address: {:#02X} - Starting Countdown",
                            game_addr
                        );

                        for i in 0..10 {
                            println!("{}", 10-i);
                            thread::sleep(time::Duration::from_secs(1));
                        }

                        return Python::with_gil(|py: Python| {
                            addrs.to_object(py)
                        });

                    }
                }
            }
        }
    }


    return Python::with_gil(|py: Python| {
        addrs.to_object(py)
    });
}

#[pyfunction]
fn get_value(addr: usize, val: usize) -> PyResult<f64> {
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
    let value;
    if val == 4 {
        value = i32::from_le_bytes(vec_to_arr(res_addr_vec)) as f64;
    } else {
        value = f64::from_le_bytes(vec_to_arr(res_addr_vec));
    }

    Ok(value)
}

/// A Python module implemented in Rust.
#[pymodule]
fn BloonsAI(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(get_value, m)?)?;
    m.add_function(wrap_pyfunction!(initialize_restart, m)?)?;
    Ok(())
}