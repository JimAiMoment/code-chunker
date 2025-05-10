#!/usr/bin/env python3
"""
Enhanced Parsing Example

This example demonstrates how to use the enhanced language parsers
and specialized configurations for different use cases.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import code_chunker
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_chunker import CodeChunker, ChunkerConfig, get_config_for_use_case


def create_typescript_react_example():
    """Create a TypeScript React example"""
    code = """
import React, { useState, useEffect } from 'react';

interface Props {
  title: string;
  children: React.ReactNode;
}

type ButtonVariant = 'primary' | 'secondary' | 'danger';

export const ThemeContext = React.createContext({ theme: 'light' });

export const useWindowSize = () => {
  const [size, setSize] = useState({ width: 0, height: 0 });
  
  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return size;
};

export const Button: React.FC<{
  variant: ButtonVariant;
  onClick: () => void;
}> = ({ variant, onClick, children }) => {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  );
};

export default function App({ title, children }: Props) {
  const size = useWindowSize();
  
  return (
    <ThemeContext.Provider value={{ theme: 'dark' }}>
      <div className="app">
        <h1>{title}</h1>
        <p>Window width: {size.width}px</p>
        {children}
      </div>
    </ThemeContext.Provider>
  );
}
"""
    return code


def create_solidity_contract_example():
    """Create a Solidity contract example"""
    code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

abstract contract Ownable {
    address private _owner;
    
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    
    constructor() {
        _owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
    }
    
    modifier onlyOwner() {
        require(_owner == msg.sender, "Ownable: caller is not the owner");
        _;
    }
    
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }
}

contract TokenVesting is Ownable {
    IERC20 public token;
    uint256 public vestingStart;
    uint256 public vestingDuration;
    
    mapping(address => uint256) public allocations;
    mapping(address => uint256) public claimed;
    
    event TokensClaimed(address indexed beneficiary, uint256 amount);
    
    constructor(address _token, uint256 _vestingDuration) {
        token = IERC20(_token);
        vestingStart = block.timestamp;
        vestingDuration = _vestingDuration;
    }
    
    function setAllocation(address beneficiary, uint256 amount) external onlyOwner {
        require(beneficiary != address(0), "Invalid address");
        require(amount > 0, "Amount must be greater than 0");
        allocations[beneficiary] = amount;
    }
    
    function claimTokens() external payable {
        uint256 allocation = allocations[msg.sender];
        require(allocation > 0, "No allocation found");
        
        uint256 elapsedTime = block.timestamp - vestingStart;
        uint256 vestedAmount;
        
        if (elapsedTime >= vestingDuration) {
            vestedAmount = allocation;
        } else {
            vestedAmount = (allocation * elapsedTime) / vestingDuration;
        }
        
        uint256 claimableAmount = vestedAmount - claimed[msg.sender];
        require(claimableAmount > 0, "No tokens to claim");
        
        claimed[msg.sender] += claimableAmount;
        require(token.transfer(msg.sender, claimableAmount), "Transfer failed");
        
        emit TokensClaimed(msg.sender, claimableAmount);
    }
}
"""
    return code


def create_go_concurrency_example():
    """Create a Go concurrency example"""
    code = """
package main

import (
	"fmt"
	"sync"
	"time"
)

// Result represents a computation result
type Result struct {
	value int
	err   error
}

// Worker represents a concurrent worker
type Worker struct {
	id        int
	jobs      chan int
	results   chan Result
	wg        sync.WaitGroup
	rateLimit chan struct{}
	mutex     sync.Mutex
}

func NewWorker(id int, jobs chan int, results chan Result) *Worker {
	return &Worker{
		id:        id,
		jobs:      jobs,
		results:   results,
		rateLimit: make(chan struct{}, 5),
	}
}

func (w *Worker) Start() {
	w.wg.Add(1)
	go func() {
		defer w.wg.Done()
		for job := range w.jobs {
			w.rateLimit <- struct{}{}
			result := w.process(job)
			w.results <- result
			<-w.rateLimit
		}
	}()
}

func (w *Worker) process(job int) Result {
	// Simulate processing time
	time.Sleep(100 * time.Millisecond)
	
	w.mutex.Lock()
	defer w.mutex.Unlock()
	
	return Result{
		value: job * 2,
		err:   nil,
	}
}

func (w *Worker) Wait() {
	w.wg.Wait()
}

func main() {
	jobs := make(chan int, 100)
	results := make(chan Result, 100)
	
	// Create workers
	numWorkers := 5
	workers := make([]*Worker, numWorkers)
	
	for i := 0; i < numWorkers; i++ {
		workers[i] = NewWorker(i, jobs, results)
		workers[i].Start()
	}
	
	// Send jobs
	go func() {
		for i := 0; i < 20; i++ {
			jobs <- i
		}
		close(jobs)
	}()
	
	// Collect results
	go func() {
		for result := range results {
			if result.err != nil {
				fmt.Printf("Error: %v\\n", result.err)
			} else {
				fmt.Printf("Result: %d\\n", result.value)
			}
		}
	}()
	
	// Wait for all workers to finish
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		for _, worker := range workers {
			worker.Wait()
		}
		close(results)
	}()
	
	wg.Wait()
	fmt.Println("All jobs completed")
}
"""
    return code


def main():
    # Create examples
    typescript_code = create_typescript_react_example()
    solidity_code = create_solidity_contract_example()
    go_code = create_go_concurrency_example()
    
    # Parse with specialized configs
    print("=== TypeScript React Parsing ===")
    ts_config = ChunkerConfig(**get_config_for_use_case('typescript', 'react'))
    ts_chunker = CodeChunker(config=ts_config)
    ts_result = ts_chunker.parse(typescript_code, language='typescript')
    
    print(f"Found {len(ts_result.chunks)} chunks:")
    for chunk in ts_result.chunks:
        chunk_type = chunk.type.value
        name = chunk.name or "unnamed"
        lines = f"lines {chunk.start_line}-{chunk.end_line}"
        
        # Print additional metadata for React components
        if hasattr(chunk.type, 'value') and chunk.type.value in ['component', 'hook', 'context']:
            metadata = ", ".join(f"{k}: {v}" for k, v in chunk.metadata.items() if v)
            print(f"  - {chunk_type}: {name} ({lines}) [{metadata}]")
        else:
            print(f"  - {chunk_type}: {name} ({lines})")
    
    print("\n=== Solidity Contract Parsing ===")
    sol_config = ChunkerConfig(**get_config_for_use_case('solidity', 'contract'))
    sol_chunker = CodeChunker(config=sol_config)
    sol_result = sol_chunker.parse(solidity_code, language='solidity')
    
    print(f"Found {len(sol_result.chunks)} chunks:")
    for chunk in sol_result.chunks:
        chunk_type = chunk.type.value
        name = chunk.name or "unnamed"
        lines = f"lines {chunk.start_line}-{chunk.end_line}"
        
        # Print visibility and modifiers for functions
        if chunk.type.value == 'function' and 'visibility' in chunk.metadata:
            visibility = chunk.metadata.get('visibility', 'internal')
            modifiers = ", ".join(chunk.metadata.get('modifiers', []))
            is_payable = "payable" if chunk.metadata.get('is_payable', False) else ""
            mod_info = f"{visibility} {is_payable} {modifiers}".strip()
            print(f"  - {chunk_type}: {name} ({lines}) [{mod_info}]")
        else:
            print(f"  - {chunk_type}: {name} ({lines})")
    
    print("\n=== Go Concurrency Parsing ===")
    go_config = ChunkerConfig(**get_config_for_use_case('go', 'performance'))
    go_chunker = CodeChunker(config=go_config)
    go_result = go_chunker.parse(go_code, language='go')
    
    print(f"Found {len(go_result.chunks)} chunks:")
    for chunk in go_result.chunks:
        chunk_type = chunk.type.value
        name = chunk.name or "unnamed"
        lines = f"lines {chunk.start_line}-{chunk.end_line}"
        
        # Print concurrency patterns for functions and methods
        if chunk.type.value in ['function', 'method'] and 'concurrency_patterns' in chunk.metadata:
            patterns = chunk.metadata.get('concurrency_patterns', {})
            if patterns:
                pattern_info = []
                if 'goroutines' in patterns:
                    pattern_info.append(f"{len(patterns['goroutines'])} goroutines")
                if 'channels' in patterns:
                    pattern_info.append(f"{len(patterns['channels'])} channel ops")
                if 'mutex_operations' in patterns:
                    pattern_info.append("mutex")
                if 'waitgroup_operations' in patterns:
                    pattern_info.append("waitgroup")
                
                concurrency_info = ", ".join(pattern_info)
                print(f"  - {chunk_type}: {name} ({lines}) [{concurrency_info}]")
            else:
                print(f"  - {chunk_type}: {name} ({lines})")
        elif chunk.type.value == 'class' and chunk.metadata.get('go_type') == 'struct':
            struct_info = []
            if chunk.metadata.get('has_mutex', False):
                struct_info.append("has mutex")
            if chunk.metadata.get('has_waitgroup', False):
                struct_info.append("has waitgroup")
            if chunk.metadata.get('has_channel', False):
                struct_info.append("has channel")
            
            if struct_info:
                print(f"  - {chunk_type}: {name} ({lines}) [{', '.join(struct_info)}]")
            else:
                print(f"  - {chunk_type}: {name} ({lines})")
        else:
            print(f"  - {chunk_type}: {name} ({lines})")


if __name__ == "__main__":
    main() 