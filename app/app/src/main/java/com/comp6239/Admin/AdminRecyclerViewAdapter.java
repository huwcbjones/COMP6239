package com.comp6239.Admin;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.comp6239.Admin.AdminApprovalFragment.OnApproveTutorFragmentInteractionListener;
import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link Tutor} and makes a call to the
 * specified {@link OnApproveTutorFragmentInteractionListener}.
 * TODO: Replace the implementation with code for your data type.
 */
public class AdminRecyclerViewAdapter extends RecyclerView.Adapter<AdminRecyclerViewAdapter.ViewHolder> {

    private List<Tutor> mValues;
    private final OnApproveTutorFragmentInteractionListener mListener;

    public AdminRecyclerViewAdapter(List<Tutor> items, OnApproveTutorFragmentInteractionListener listener) {
        mValues = items;
        mListener = listener;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.admin_approval_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.mIdView.setText(mValues.get(position).getFirstName());
        holder.mContentView.setText(mValues.get(position).getLastName());

        holder.mView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (null != mListener) {
                    // Notify the active callbacks interface (the activity, if the
                    // fragment is attached to one) that an item has been selected.
                    mListener.onApproveTutorFragmentInteraction(holder.mItem);
                }
            }
        });
    }

    @Override
    public int getItemCount() {
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public final View mView;
        public final TextView mIdView;
        public final TextView mContentView;
        public Tutor mItem;

        public ViewHolder(View view) {
            super(view);
            mView = view;
            mIdView = (TextView) view.findViewById(R.id.subject_name);
            mContentView = (TextView) view.findViewById(R.id.subject_id);
        }

        @Override
        public String toString() {
            return super.toString() + " '" + mContentView.getText() + "'";
        }
    }
}
