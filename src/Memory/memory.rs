/*
Credit: https://github.com/Lonami/memo/tree/master
*/


use crate::scan::{Region, Scan, Scannable};
use winapi::um::winnt;
use std::mem::{self, MaybeUninit};
use winapi::shared::minwindef::{DWORD, FALSE, HMODULE};
use std::io;
use winapi::ctypes::c_void;
use std::ptr::{self, NonNull};
use winapi::um::winnt::MEMORY_BASIC_INFORMATION;


// How many process identifiers will be enumerated at most.
const MAX_PIDS: usize = 1024;

/// How many ASCII characters to read for a process name at most.
const MAX_PROC_NAME_LEN: usize = 64;

/// A handle to an opened process.
#[derive(Debug)]
pub struct Process {
    pid: u32,
    handle: NonNull<c_void>,
}

/// Enumerate the process identifiers of all programs currently running.
pub fn enum_proc() -> io::Result<Vec<u32>> {
    let mut size = 0;
    let mut pids = Vec::<DWORD>::with_capacity(MAX_PIDS);
    // SAFETY: the pointer is valid and the size matches the capacity.
    if unsafe {
        winapi::um::psapi::EnumProcesses(
            pids.as_mut_ptr(),
            (pids.capacity() * mem::size_of::<DWORD>()) as u32,
            &mut size,
        )
    } == FALSE
    {
        return Err(io::Error::last_os_error());
    }

    let count = size as usize / mem::size_of::<DWORD>();
    // SAFETY: the call succeeded and count equals the right amount of items.
    unsafe { pids.set_len(count) };
    Ok(pids)
}

impl Process {
    /// Open a process handle given its process identifier.
    pub fn open(pid: u32) -> io::Result<Self> {
        // SAFETY: the call doesn't have dangerous side-effects
        NonNull::new(unsafe {
            winapi::um::processthreadsapi::OpenProcess(
                winnt::PROCESS_QUERY_INFORMATION | winnt::PROCESS_VM_READ,
                FALSE,
                pid,
            )
        })
        .map(|handle| Self { pid, handle })
        .ok_or_else(io::Error::last_os_error)
    }

    /// Return the process identifier.
    pub fn pid(&self) -> u32 {
        self.pid
    }

    /// Return the base name of the first module loaded by this process.
    pub fn name(&self) -> io::Result<String> {
        let mut module = MaybeUninit::<HMODULE>::uninit();
        let mut size = 0;
        // SAFETY: the pointer is valid and the size is correct.
        if unsafe {
            winapi::um::psapi::EnumProcessModules(
                self.handle.as_ptr(),
                module.as_mut_ptr(),
                mem::size_of::<HMODULE>() as u32,
                &mut size,
            )
        } == FALSE
        {
            return Err(io::Error::last_os_error());
        }

        // SAFETY: the call succeeded, so module is initialized.
        let module = unsafe { module.assume_init() };

        let mut buffer = Vec::<u8>::with_capacity(MAX_PROC_NAME_LEN);
        // SAFETY: the handle, module and buffer are all valid.
        let length = unsafe {
            winapi::um::psapi::GetModuleBaseNameA(
                self.handle.as_ptr(),
                module,
                buffer.as_mut_ptr().cast(),
                buffer.capacity() as u32,
            )
        };
        if length == 0 {
            return Err(io::Error::last_os_error());
        }

        // SAFETY: the call succeeded and length represents bytes.
        unsafe { buffer.set_len(length as usize) };
        Ok(String::from_utf8(buffer).unwrap())
    }

    pub fn enum_modules(&self) -> io::Result<Vec<winapi::shared::minwindef::HMODULE>> {
        let mut size = 0;
        // SAFETY: the pointer is valid and the indicated size is 0.
        if unsafe {
            winapi::um::psapi::EnumProcessModules(
                self.handle.as_ptr(),
                ptr::null_mut(),
                0,
                &mut size,
            )
        } == FALSE
        {
            return Err(io::Error::last_os_error());
        }

        let mut modules = Vec::with_capacity(size as usize / mem::size_of::<HMODULE>());
        // SAFETY: the pointer is valid and the size is correct.
        if unsafe {
            winapi::um::psapi::EnumProcessModules(
                self.handle.as_ptr(),
                modules.as_mut_ptr(),
                (modules.capacity() * mem::size_of::<HMODULE>()) as u32,
                &mut size,
            )
        } == FALSE
        {
            return Err(io::Error::last_os_error());
        }

        // SAFETY: the call succeeded, so modules up to `size` are initialized.
        unsafe {
            modules.set_len(size as usize / mem::size_of::<HMODULE>());
        }

        Ok(modules)
    }

    pub fn memory_regions(&self) -> Vec<MEMORY_BASIC_INFORMATION> {
        let mut base = 0;
        let mut regions = Vec::new();
        let mut info = MaybeUninit::uninit();

        loop {
            // SAFETY: the info structure points to valid memory.
            let written = unsafe {
                winapi::um::memoryapi::VirtualQueryEx(
                    self.handle.as_ptr(),
                    base as *const _,
                    info.as_mut_ptr(),
                    mem::size_of::<MEMORY_BASIC_INFORMATION>(),
                )
            };
            if written == 0 {
                break regions;
            }
            // SAFETY: a non-zero amount was written to the structure
            let info = unsafe { info.assume_init() };
            base = info.BaseAddress as usize + info.RegionSize;
            regions.push(info);
        }
    }

    pub fn base_memory_regions(&self) -> io::Result<Vec<MEMORY_BASIC_INFORMATION>> {
        let modules = self.enum_modules()?;
        let regions = self.memory_regions();
        Ok(modules
            .iter()
            .flat_map(|module| {
                regions
                    .iter()
                    .find(|region| {
                        let base = region.AllocationBase as usize;
                        let addr = *module as usize;
                        base == addr
                    })
                    .copied()
            })
            .collect())
    }

    pub fn read_memory(&self, addr: usize, n: usize) -> io::Result<Vec<u8>> {
        let mut buffer = Vec::<u8>::with_capacity(n);
        let mut read = 0;

        // SAFETY: the buffer points to valid memory, and the buffer size is correctly set.
        if unsafe {
            winapi::um::memoryapi::ReadProcessMemory(
                self.handle.as_ptr(),
                addr as *const _,
                buffer.as_mut_ptr().cast(),
                buffer.capacity(),
                &mut read,
            )
        } == FALSE
        {
            Err(io::Error::last_os_error())
        } else {
            // SAFETY: the call succeeded and `read` contains the amount of bytes written.
            unsafe { buffer.set_len(read as usize) };
            Ok(buffer)
        }
    }

    pub fn scan_regions<T: Scannable>(
        &self,
        regions: &[MEMORY_BASIC_INFORMATION],
        scan: Scan<T>,
    ) -> Vec<Region> {
        regions
            .iter()
            .flat_map(
                |region| match self.read_memory(region.BaseAddress as _, region.RegionSize) {
                    Ok(memory) => Some(scan.run(region.clone(), memory)),
                    Err(err) => {
                        // eprintln!(
                        //     "Failed to read {} bytes at {:?}: {}",
                        //     region.RegionSize, region.BaseAddress, err,
                        // );
                        None
                    }
                },
            )
            .collect()
    }
}

impl Drop for Process {
    fn drop(&mut self) {
        // SAFETY: the handle is valid and non-null
        let ret = unsafe { winapi::um::handleapi::CloseHandle(self.handle.as_mut()) };
        assert_ne!(ret, FALSE);
    }
}