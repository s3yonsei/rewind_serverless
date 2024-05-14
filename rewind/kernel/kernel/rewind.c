#include <linux/syscalls.h>
#include <linux/kernel.h>
#include <linux/linkage.h>
#include <linux/sched.h>
#include <linux/kthread.h>
#include <linux/signal.h>
#include <linux/mm_rewind.h>
#include <asm/msr.h>

#include <linux/cpu.h>
#include <linux/cpufreq.h>
#include <linux/smp.h>

static void rewind_threads(void)
{
	struct task_struct *tsk;
	int err;

	if (current->rewind_nr_threads == get_nr_threads(current))
		return;

	err = rewind_de_thread(current);
	if (err) {
		printk(KERN_INFO "REWIND(RW): de thread error %d\n", err);
	}

	list_for_each_entry(tsk, &current->children, sibling) {
		send_sig (SIGKILL, tsk, 0);
	}
}


SYSCALL_DEFINE1(checkpoint, unsigned long __user, num)	// syscall(548)
{
	struct task_struct *tsk = current;
	unsigned long flags;
	unsigned long checktime;

	if (num > 0)
		checktime = ktime_get_real_ns();

	tsk->rewind_cp = 0;
	tsk->rewind_cnt = 1;
	tsk->rewind_pte_cnt = 0;
	tsk->mm->rewindable = 1;

	if (lock_task_sighand(tsk, &flags)) {
		tsk->rewind_nr_threads = get_nr_threads(tsk);
		unlock_task_sighand(tsk, &flags);
	}
	
	copy_pgt(tsk->mm, DO_CHECKPOINT);

	tsk->rewind_vma_reuse = 0;
	tsk->rewind_vma_alloc = 0;

	if (num > 0) {
		checktime = ktime_get_real_ns() - checktime;
		printk(KERN_INFO "(REWIND) checkpoint time: %lu\n", checktime);
	}
	
	return 0;
}

SYSCALL_DEFINE1(rewind, unsigned long __user, num)	// syscall(549)
{
	struct task_struct *tsk = current;
	unsigned long rewindtime;

	if (num > 0)
		rewindtime = ktime_get_real_ns();

	rewind_threads();
	
	tsk->rewind_pte = 0;
	tsk->rewind_clear = 0;
	tsk->rewind_unmap = 0;
	tsk->rewind_flush = 0;
	tsk->rewind_page_cnt = 0;
	tsk->rewind_pte_cnt = 0;
	tsk->rewind_total_vma = 0;
	tsk->rewind_unused_vma = 0;
	tsk->rewind_vma = 0;
	tsk->rewind_page_reuse = 0;
	tsk->rewind_reusable_size = 0;
	tsk->rewind_page_erase_cnt = 0;
	tsk->rewind_page_cow_cnt = 0;
	tsk->rewind_cnt++;

	copy_pgt(tsk->mm, DO_REWIND); // return type int (have to if state)
	
	tsk->rewind_vma_reuse = 0;
        tsk->rewind_vma_alloc = 0;
	tsk->rewind_reused_page = 0;
	tsk->rewind_reused_size = 0;

	if (num > 0) {
		rewindtime = ktime_get_real_ns() - rewindtime;
		printk(KERN_INFO "(REWIND) rewind time: %lu\n", rewindtime);
	}

	return 0;
}

SYSCALL_DEFINE0(rewindable)	// syscall(550)
{
	current->real_parent->rewind_parent = 1;
	
	return 0;
}
